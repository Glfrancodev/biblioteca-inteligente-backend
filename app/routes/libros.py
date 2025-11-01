from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.usuario import Usuario
from app.models.libro import Libro, Editorial, Autor, AutorLibro
from app.schemas.libro import (
    LibroCreate,
    LibroUpdate,
    LibroResponse,
    EditorialCreate,
    EditorialResponse,
    AutorCreate,
    AutorResponse
)
from app.services.auth import get_current_active_user
from app.services.s3_service import s3_service
from app.services.google_books_service import google_books_service
from app.utils.responses import create_success_response, create_error_response, ErrorCodes

router = APIRouter(prefix="/libros", tags=["Libros"])
editorial_router = APIRouter(prefix="/editoriales", tags=["Editoriales"])
autor_router = APIRouter(prefix="/autores", tags=["Autores"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])


# ENDPOINTS DE LIBROS
@router.post("/with-file", status_code=status.HTTP_201_CREATED)
async def create_libro_with_file(
    titulo: str = Form(...),
    totalPaginas: int = Form(...),
    sinopsis: str = Form(...),
    idEditorial: int = Form(...),
    autores_ids: str = Form(...),  # JSON string: "[1,2,3]"
    urlPortada: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo libro con archivo PDF adjunto"""
    import json
    
    # Parsear autores_ids
    print(f"📥 autores_ids recibido (tipo: {type(autores_ids)}): {autores_ids}")
    try:
        # Si ya es una lista
        if isinstance(autores_ids, list):
            autores_ids_list = autores_ids
        elif isinstance(autores_ids, int):
            # Si es un número directamente
            autores_ids_list = [autores_ids]
        elif isinstance(autores_ids, str):
            # Es string, manejar diferentes formatos
            autores_ids = autores_ids.strip()
            
            # Si es "1,2,3" (sin corchetes), agregar corchetes
            if autores_ids and not autores_ids.startswith('['):
                autores_ids = f"[{autores_ids}]"
            
            # Intentar parsear como JSON
            parsed = json.loads(autores_ids)
            
            # Si el resultado es un número, convertir a lista
            if isinstance(parsed, int):
                autores_ids_list = [parsed]
            elif isinstance(parsed, list):
                autores_ids_list = parsed
            else:
                raise ValueError("El resultado debe ser un número o una lista")
        else:
            raise ValueError("Formato inválido")
            
        print(f"✓ autores_ids parseado: {autores_ids_list}")
    except Exception as e:
        print(f"❌ Error al parsear autores_ids: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"autores_ids debe ser un array JSON válido. Ejemplo: [1,2,3] o '1,2,3'. Error: {str(e)}"
        )
    
    # Verificar que la editorial existe
    editorial = db.query(Editorial).filter(Editorial.idEditorial == idEditorial).first()
    if not editorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.EDITORIAL_NOT_FOUND,
                "Editorial no encontrada"
            )
        )
    
    # Verificar que los autores existen
    print(f"🔍 Verificando autores: {autores_ids_list}")
    autores = db.query(Autor).filter(Autor.idAutor.in_(autores_ids_list)).all()
    print(f"✓ Autores encontrados: {len(autores)}")
    if len(autores) != len(autores_ids_list):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.AUTHOR_NOT_FOUND,
                "Uno o más autores no encontrados"
            )
        )
    
    # Subir archivo a S3 y obtener URL firmada
    print(f"📤 Subiendo archivo a S3...")
    try:
        s3_key, signed_url = s3_service.upload_file(file, folder="libros", custom_filename=titulo)
        print(f"✅ Archivo subido: {s3_key}")
    except Exception as e:
        print(f"❌ Error al subir a S3: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorCodes.INTERNAL_ERROR,
                f"Error al subir archivo a S3: {str(e)}"
            )
        )
    
    # Crear libro con la key de S3 (no la URL firmada, porque expira)
    print(f"📚 Creando libro en BD...")
    try:
        db_libro = Libro(
            titulo=titulo,
            totalPaginas=totalPaginas,
            sinopsis=sinopsis,
            urlLibro=s3_key,  # Guardamos la key, no la URL
            urlPortada=urlPortada,  # URL de portada de Google Books
            idEditorial=idEditorial
        )
        
        db.add(db_libro)
        db.commit()
        db.refresh(db_libro)
        print(f"✅ Libro creado con ID: {db_libro.idLibro}")
    except Exception as e:
        print(f"❌ Error al crear libro: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorCodes.INTERNAL_ERROR,
                f"Error al crear libro en BD: {str(e)}"
            )
        )
    
    # Asociar autores al libro
    for autor_id in autores_ids_list:
        autor_libro = AutorLibro(idAutor=autor_id, idLibro=db_libro.idLibro)
        db.add(autor_libro)
    
    db.commit()
    db.refresh(db_libro)
    
    # Construir respuesta con autores
    response = LibroResponse.model_validate(db_libro)
    response.autores = [AutorResponse.model_validate(al.autor) for al in db_libro.autor_libros]
    
    libro_dict = response.model_dump()
    # Agregar URL firmada a la respuesta (no se guarda en BD)
    libro_dict["url_firmada"] = signed_url
    
    return create_success_response(
        data=libro_dict,
        message="Libro creado exitosamente con archivo PDF"
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_libro(
    libro: LibroCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo libro (sin archivo)"""
    # Verificar que la editorial existe
    editorial = db.query(Editorial).filter(Editorial.idEditorial == libro.idEditorial).first()
    if not editorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.EDITORIAL_NOT_FOUND,
                "Editorial no encontrada"
            )
        )
    
    # Verificar que los autores existen
    autores = db.query(Autor).filter(Autor.idAutor.in_(libro.autores_ids)).all()
    if len(autores) != len(libro.autores_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.AUTHOR_NOT_FOUND,
                "Uno o más autores no encontrados"
            )
        )
    
    # Crear libro
    db_libro = Libro(
        titulo=libro.titulo,
        totalPaginas=libro.totalPaginas,
        sinopsis=libro.sinopsis,
        urlLibro=libro.urlLibro,
        idEditorial=libro.idEditorial
    )
    
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    
    # Asociar autores al libro
    for autor_id in libro.autores_ids:
        autor_libro = AutorLibro(idAutor=autor_id, idLibro=db_libro.idLibro)
        db.add(autor_libro)
    
    db.commit()
    db.refresh(db_libro)
    
    # Construir respuesta con autores
    response = LibroResponse.model_validate(db_libro)
    response.autores = [AutorResponse.model_validate(al.autor) for al in db_libro.autor_libros]
    
    libro_dict = response.model_dump()
    return create_success_response(
        data=libro_dict,
        message="Libro creado exitosamente"
    )


@router.get("")
def read_libros(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de libros"""
    libros = db.query(Libro).offset(skip).limit(limit).all()
    
    # Construir respuestas con autores
    responses = []
    for libro in libros:
        response = LibroResponse.model_validate(libro)
        response.autores = [AutorResponse.model_validate(al.autor) for al in libro.autor_libros]
        responses.append(response.model_dump())
    
    return create_success_response(
        data=responses,
        message=f"{len(responses)} libros obtenidos exitosamente"
    )


@router.get("/{libro_id}")
def read_libro(libro_id: int, db: Session = Depends(get_db)):
    """Obtener un libro por ID"""
    libro = db.query(Libro).filter(Libro.idLibro == libro_id).first()
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.BOOK_NOT_FOUND,
                "Libro no encontrado"
            )
        )
    
    response = LibroResponse.model_validate(libro)
    response.autores = [AutorResponse.model_validate(al.autor) for al in libro.autor_libros]
    
    libro_dict = response.model_dump()
    
    # Si tiene URL en S3, generar URL firmada
    if libro.urlLibro:
        try:
            libro_dict["url_firmada"] = s3_service.generate_presigned_url(libro.urlLibro)
        except:
            libro_dict["url_firmada"] = None
    else:
        libro_dict["url_firmada"] = None
    
    return create_success_response(
        data=libro_dict,
        message="Libro obtenido exitosamente"
    )


@router.put("/{libro_id}")
def update_libro(
    libro_id: int,
    libro_update: LibroUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Actualizar un libro"""
    db_libro = db.query(Libro).filter(Libro.idLibro == libro_id).first()
    if not db_libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.BOOK_NOT_FOUND,
                "Libro no encontrado"
            )
        )
    
    update_data = libro_update.model_dump(exclude_unset=True)
    
    # Manejar actualización de autores
    if "autores_ids" in update_data:
        autores_ids = update_data.pop("autores_ids")
        # Eliminar asociaciones existentes
        db.query(AutorLibro).filter(AutorLibro.idLibro == libro_id).delete()
        # Crear nuevas asociaciones
        for autor_id in autores_ids:
            autor_libro = AutorLibro(idAutor=autor_id, idLibro=libro_id)
            db.add(autor_libro)
    
    # Actualizar otros campos
    for field, value in update_data.items():
        setattr(db_libro, field, value)
    
    db.commit()
    db.refresh(db_libro)
    
    response = LibroResponse.model_validate(db_libro)
    response.autores = [AutorResponse.model_validate(al.autor) for al in db_libro.autor_libros]
    
    libro_dict = response.model_dump()
    return create_success_response(
        data=libro_dict,
        message="Libro actualizado exitosamente"
    )


@router.delete("/{libro_id}")
def delete_libro(
    libro_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Eliminar un libro y su archivo de S3 si existe"""
    db_libro = db.query(Libro).filter(Libro.idLibro == libro_id).first()
    if not db_libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.BOOK_NOT_FOUND,
                "Libro no encontrado"
            )
        )
    
    # Si el libro tiene archivo en S3, eliminarlo
    s3_deleted = False
    if db_libro.urlLibro:
        try:
            print(f"🗑️ Eliminando archivo de S3: {db_libro.urlLibro}")
            s3_service.delete_file(db_libro.urlLibro)
            s3_deleted = True
            print(f"✅ Archivo eliminado de S3 correctamente")
        except Exception as e:
            print(f"⚠️ Error al eliminar archivo de S3: {str(e)}")
            # Continuar con la eliminación del libro en BD
            # (puedes decidir si quieres lanzar excepción o solo advertir)
    
    # Eliminar libro de la base de datos
    db.delete(db_libro)
    db.commit()
    
    return create_success_response(
        data={
            "deleted": True,
            "id": libro_id,
            "s3_file_deleted": s3_deleted
        },
        message="Libro eliminado exitosamente" + (" (incluyendo archivo de S3)" if s3_deleted else "")
    )


# ENDPOINTS DE EDITORIALES
@editorial_router.post("", status_code=status.HTTP_201_CREATED)
def create_editorial(
    editorial: EditorialCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear una nueva editorial"""
    db_editorial = Editorial(nombre=editorial.nombre)
    db.add(db_editorial)
    db.commit()
    db.refresh(db_editorial)
    
    editorial_dict = EditorialResponse.model_validate(db_editorial).model_dump()
    return create_success_response(
        data=editorial_dict,
        message="Editorial creada exitosamente"
    )


@editorial_router.get("")
def read_editoriales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de editoriales"""
    editoriales = db.query(Editorial).offset(skip).limit(limit).all()
    editoriales_dict = [EditorialResponse.model_validate(e).model_dump() for e in editoriales]
    
    return create_success_response(
        data=editoriales_dict,
        message=f"{len(editoriales_dict)} editoriales obtenidas exitosamente"
    )


# ENDPOINTS DE AUTORES
@autor_router.post("", status_code=status.HTTP_201_CREATED)
def create_autor(
    autor: AutorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo autor"""
    db_autor = Autor(nombre=autor.nombre)
    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    
    autor_dict = AutorResponse.model_validate(db_autor).model_dump()
    return create_success_response(
        data=autor_dict,
        message="Autor creado exitosamente"
    )


@autor_router.get("")
def read_autores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de autores"""
    autores = db.query(Autor).offset(skip).limit(limit).all()
    autores_dict = [AutorResponse.model_validate(a).model_dump() for a in autores]
    
    return create_success_response(
        data=autores_dict,
        message=f"{len(autores_dict)} autores obtenidos exitosamente"
    )


# ENDPOINTS DE ADMINISTRACIÓN
def populate_books_task(total_books: int, db: Session):
    """Tarea en background para poblar la BD"""
    try:
        print(f"🚀 Iniciando población de {total_books} libros...")
        
        # Obtener libros de Google Books
        books_data = google_books_service.get_programming_books(total_books=total_books)
        
        stats = {
            "libros_insertados": 0,
            "libros_duplicados": 0,
            "autores_nuevos": 0,
            "editoriales_nuevas": 0,
            "errores": 0
        }
        
        for book_meta in books_data:
            try:
                # 1. CREAR O BUSCAR EDITORIAL
                editorial = db.query(Editorial).filter(
                    Editorial.nombre == book_meta["editorial"]
                ).first()
                
                if not editorial:
                    editorial = Editorial(nombre=book_meta["editorial"])
                    db.add(editorial)
                    db.flush()
                    stats["editoriales_nuevas"] += 1
                
                # 2. VERIFICAR SI EL LIBRO YA EXISTE (por título y editorial)
                libro_existente = db.query(Libro).filter(
                    Libro.titulo == book_meta["titulo"],
                    Libro.idEditorial == editorial.idEditorial
                ).first()
                
                if libro_existente:
                    stats["libros_duplicados"] += 1
                    continue
                
                # 3. CREAR LIBRO (urlLibro = NULL, pero con urlPortada de Google Books)
                libro = Libro(
                    titulo=book_meta["titulo"],
                    totalPaginas=book_meta["paginas_totales"],
                    sinopsis=book_meta["sinopsis"],
                    urlLibro=None,  # Sin PDF
                    urlPortada=book_meta.get("portada_url"),  # URL de portada de Google Books
                    idEditorial=editorial.idEditorial
                )
                db.add(libro)
                db.flush()
                stats["libros_insertados"] += 1
                
                # 4. CREAR O BUSCAR AUTORES Y RELACIONAR
                for autor_nombre in book_meta["autores"]:
                    autor = db.query(Autor).filter(
                        Autor.nombre == autor_nombre
                    ).first()
                    
                    if not autor:
                        autor = Autor(nombre=autor_nombre)
                        db.add(autor)
                        db.flush()
                        stats["autores_nuevos"] += 1
                    
                    # Crear relación AutorLibro
                    autor_libro = AutorLibro(
                        idLibro=libro.idLibro,
                        idAutor=autor.idAutor
                    )
                    db.add(autor_libro)
                
                # Commit cada 50 libros para evitar transacciones muy grandes
                if stats["libros_insertados"] % 50 == 0:
                    db.commit()
                    print(f"  ✓ {stats['libros_insertados']} libros insertados...")
                
            except Exception as e:
                print(f"⚠️ Error al insertar libro '{book_meta.get('titulo', 'Unknown')}': {str(e)}")
                stats["errores"] += 1
                db.rollback()
                continue
        
        # Commit final
        db.commit()
        
        print(f"\n✅ Población completada:")
        print(f"  - Libros insertados: {stats['libros_insertados']}")
        print(f"  - Libros duplicados (omitidos): {stats['libros_duplicados']}")
        print(f"  - Autores nuevos: {stats['autores_nuevos']}")
        print(f"  - Editoriales nuevas: {stats['editoriales_nuevas']}")
        print(f"  - Errores: {stats['errores']}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error grave en población: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@admin_router.post("/populate-books")
def populate_books_from_google(
    total_books: int = 1000,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Poblar la base de datos con libros desde Google Books API
    
    Args:
        total_books: Cantidad de libros a insertar (default: 1000)
    
    Returns:
        Mensaje de confirmación (se ejecuta en background)
    """
    if total_books > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El máximo de libros por operación es 5000"
        )
    
    # Ejecutar en background si está disponible
    if background_tasks:
        background_tasks.add_task(populate_books_task, total_books, db)
        return create_success_response(
            data={
                "status": "En proceso",
                "total_solicitado": total_books,
                "mensaje": "La población de libros se está ejecutando en segundo plano"
            },
            message="Proceso de población iniciado"
        )
    else:
        # Ejecutar síncronamente (para testing)
        stats = populate_books_task(total_books, db)
        return create_success_response(
            data=stats,
            message=f"Se insertaron {stats['libros_insertados']} libros exitosamente"
        )


@admin_router.get("/populate-status")
def get_populate_status(db: Session = Depends(get_db)):
    """Obtener estadísticas de la base de datos"""
    total_libros = db.query(Libro).count()
    total_autores = db.query(Autor).count()
    total_editoriales = db.query(Editorial).count()
    libros_con_pdf = db.query(Libro).filter(Libro.urlLibro != None).count()
    libros_sin_pdf = db.query(Libro).filter(Libro.urlLibro == None).count()
    
    return create_success_response(
        data={
            "total_libros": total_libros,
            "total_autores": total_autores,
            "total_editoriales": total_editoriales,
            "libros_con_pdf": libros_con_pdf,
            "libros_sin_pdf": libros_sin_pdf
        },
        message="Estadísticas obtenidas exitosamente"
    )
