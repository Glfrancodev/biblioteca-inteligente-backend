from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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
from app.utils.responses import create_success_response, create_error_response, ErrorCodes

router = APIRouter(prefix="/libros", tags=["Libros"])
editorial_router = APIRouter(prefix="/editoriales", tags=["Editoriales"])
autor_router = APIRouter(prefix="/autores", tags=["Autores"])


# ENDPOINTS DE LIBROS
@router.post("", status_code=status.HTTP_201_CREATED)
def create_libro(
    libro: LibroCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo libro"""
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
    """Eliminar un libro"""
    db_libro = db.query(Libro).filter(Libro.idLibro == libro_id).first()
    if not db_libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.BOOK_NOT_FOUND,
                "Libro no encontrado"
            )
        )
    
    db.delete(db_libro)
    db.commit()
    
    return create_success_response(
        data={"deleted": True, "id": libro_id},
        message="Libro eliminado exitosamente"
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
