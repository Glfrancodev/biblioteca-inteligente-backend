from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.usuario import Usuario
from app.models.lectura import Lectura
from app.models.libro import Libro
from app.schemas.lectura import (
    LecturaCreate,
    LecturaUpdate,
    LecturaResponse,
    LecturaDetailResponse
)
from app.services.auth import get_current_active_user
from app.utils.responses import create_success_response, create_error_response, ErrorCodes

router = APIRouter(prefix="/lecturas", tags=["Lecturas"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_lectura(
    lectura: LecturaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear una nueva lectura para el usuario actual"""
    # Verificar que el libro existe
    libro = db.query(Libro).filter(Libro.idLibro == lectura.idLibro).first()
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.BOOK_NOT_FOUND,
                "Libro no encontrado"
            )
        )
    
    # Verificar que el usuario no tenga ya una lectura de este libro
    lectura_existente = db.query(Lectura).filter(
        Lectura.idUsuario == current_user.idUsuario,
        Lectura.idLibro == lectura.idLibro
    ).first()
    
    if lectura_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                ErrorCodes.READING_ALREADY_EXISTS,
                "Ya tienes una lectura registrada para este libro"
            )
        )
    
    # Crear lectura
    db_lectura = Lectura(
        paginaLeidas=lectura.paginaLeidas,
        estado=lectura.estado,
        idUsuario=current_user.idUsuario,
        idLibro=lectura.idLibro
    )
    
    db.add(db_lectura)
    db.commit()
    db.refresh(db_lectura)
    
    lectura_dict = LecturaResponse.model_validate(db_lectura).model_dump()
    return create_success_response(
        data=lectura_dict,
        message="Lectura creada exitosamente"
    )


@router.get("")
def read_lecturas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener todas las lecturas del usuario actual"""
    lecturas = db.query(Lectura).filter(
        Lectura.idUsuario == current_user.idUsuario
    ).offset(skip).limit(limit).all()
    
    # Construir respuesta detallada
    responses = []
    for lectura in lecturas:
        response = LecturaDetailResponse.model_validate(lectura)
        response.libro_titulo = lectura.libro.titulo
        response.libro_total_paginas = lectura.libro.totalPaginas
        
        # Calcular progreso
        if lectura.libro.totalPaginas > 0:
            response.progreso_porcentaje = (lectura.paginaLeidas / lectura.libro.totalPaginas) * 100
        else:
            response.progreso_porcentaje = 0
        
        responses.append(response.model_dump())
    
    return create_success_response(
        data=responses,
        message="Lecturas obtenidas exitosamente",
        count=len(responses)
    )


@router.get("/{lectura_id}")
def read_lectura(
    lectura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener una lectura específica"""
    lectura = db.query(Lectura).filter(
        Lectura.idLectura == lectura_id,
        Lectura.idUsuario == current_user.idUsuario
    ).first()
    
    if not lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.READING_NOT_FOUND,
                "Lectura no encontrada"
            )
        )
    
    response = LecturaDetailResponse.model_validate(lectura)
    response.libro_titulo = lectura.libro.titulo
    response.libro_total_paginas = lectura.libro.totalPaginas
    
    if lectura.libro.totalPaginas > 0:
        response.progreso_porcentaje = (lectura.paginaLeidas / lectura.libro.totalPaginas) * 100
    else:
        response.progreso_porcentaje = 0
    
    lectura_dict = response.model_dump()
    return create_success_response(
        data=lectura_dict,
        message="Lectura obtenida exitosamente",
        count=1
    )


@router.put("/{lectura_id}")
def update_lectura(
    lectura_id: int,
    lectura_update: LecturaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Actualizar el progreso de una lectura"""
    db_lectura = db.query(Lectura).filter(
        Lectura.idLectura == lectura_id,
        Lectura.idUsuario == current_user.idUsuario
    ).first()
    
    if not db_lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.READING_NOT_FOUND,
                "Lectura no encontrada"
            )
        )
    
    # Validar que las páginas leídas no excedan el total
    update_data = lectura_update.model_dump(exclude_unset=True)
    if "paginaLeidas" in update_data:
        libro = db.query(Libro).filter(Libro.idLibro == db_lectura.idLibro).first()
        if update_data["paginaLeidas"] > libro.totalPaginas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    ErrorCodes.PAGES_EXCEED_TOTAL,
                    f"Las páginas leídas no pueden exceder el total ({libro.totalPaginas})"
                )
            )
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(db_lectura, field, value)
    
    db.commit()
    db.refresh(db_lectura)
    
    lectura_dict = LecturaResponse.model_validate(db_lectura).model_dump()
    return create_success_response(
        data=lectura_dict,
        message="Lectura actualizada exitosamente"
    )


@router.delete("/{lectura_id}")
def delete_lectura(
    lectura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Eliminar una lectura"""
    db_lectura = db.query(Lectura).filter(
        Lectura.idLectura == lectura_id,
        Lectura.idUsuario == current_user.idUsuario
    ).first()
    
    if not db_lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.READING_NOT_FOUND,
                "Lectura no encontrada"
            )
        )
    
    db.delete(db_lectura)
    db.commit()
    
    return create_success_response(
        data={"deleted": True, "id": lectura_id},
        message="Lectura eliminada exitosamente"
    )


# NUEVOS ENDPOINTS DE ESTADÍSTICAS

@router.get("/estado/completados")
def get_libros_completados(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener todos los libros completados del usuario actual"""
    from app.models.lectura import EstadoLectura
    from app.services.s3_service import s3_service
    
    lecturas_completadas = db.query(Lectura).filter(
        Lectura.idUsuario == current_user.idUsuario,
        Lectura.estado == EstadoLectura.COMPLETADO
    ).offset(skip).limit(limit).all()
    
    # Construir respuesta detallada
    responses = []
    for lectura in lecturas_completadas:
        response = LecturaDetailResponse.model_validate(lectura)
        response.libro_titulo = lectura.libro.titulo
        response.libro_total_paginas = lectura.libro.totalPaginas
        response.progreso_porcentaje = 100.0  # Siempre 100% porque está completado
        
        # Convertir a dict para añadir campos adicionales
        lectura_dict = response.model_dump()
        
        # Añadir URL firmada si el libro tiene archivo en S3
        if lectura.libro.urlLibro:
            try:
                lectura_dict["url_firmada"] = s3_service.generate_presigned_url(lectura.libro.urlLibro)
            except:
                lectura_dict["url_firmada"] = None
        else:
            lectura_dict["url_firmada"] = None
        
        # Añadir URL de portada
        lectura_dict["urlPortada"] = lectura.libro.urlPortada if lectura.libro.urlPortada else None
        
        responses.append(lectura_dict)
    
    return create_success_response(
        data=responses,
        message="Libros completados obtenidos exitosamente",
        count=len(responses)
    )


@router.get("/estado/en-progreso")
def get_libros_en_progreso(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener todos los libros en progreso del usuario actual"""
    from app.models.lectura import EstadoLectura
    from app.services.s3_service import s3_service
    
    lecturas_en_progreso = db.query(Lectura).filter(
        Lectura.idUsuario == current_user.idUsuario,
        Lectura.estado == EstadoLectura.EN_PROGRESO
    ).offset(skip).limit(limit).all()
    
    # Construir respuesta detallada
    responses = []
    for lectura in lecturas_en_progreso:
        response = LecturaDetailResponse.model_validate(lectura)
        response.libro_titulo = lectura.libro.titulo
        response.libro_total_paginas = lectura.libro.totalPaginas
        
        # Calcular progreso
        if lectura.libro.totalPaginas > 0:
            response.progreso_porcentaje = (lectura.paginaLeidas / lectura.libro.totalPaginas) * 100
        else:
            response.progreso_porcentaje = 0
        
        # Convertir a dict para añadir campos adicionales
        lectura_dict = response.model_dump()
        
        # Añadir URL firmada si el libro tiene archivo en S3
        if lectura.libro.urlLibro:
            try:
                lectura_dict["url_firmada"] = s3_service.generate_presigned_url(lectura.libro.urlLibro)
            except:
                lectura_dict["url_firmada"] = None
        else:
            lectura_dict["url_firmada"] = None
        
        # Añadir URL de portada
        lectura_dict["urlPortada"] = lectura.libro.urlPortada if lectura.libro.urlPortada else None
        
        responses.append(lectura_dict)
    
    return create_success_response(
        data=responses,
        message="Libros en progreso obtenidos exitosamente",
        count=len(responses)
    )


@router.get("/estadisticas/paginas-leidas")
def get_total_paginas_leidas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener el total de páginas leídas por el usuario actual"""
    from sqlalchemy import func
    
    # Sumar todas las páginas leídas del usuario
    total_paginas = db.query(
        func.sum(Lectura.paginaLeidas)
    ).filter(
        Lectura.idUsuario == current_user.idUsuario
    ).scalar()
    
    # Si no hay lecturas, devolver 0
    total_paginas = total_paginas if total_paginas else 0
    
    # Contar total de lecturas para contexto adicional
    total_lecturas = db.query(Lectura).filter(
        Lectura.idUsuario == current_user.idUsuario
    ).count()
    
    # Calcular promedio de páginas por lectura
    promedio_paginas = total_paginas / total_lecturas if total_lecturas > 0 else 0
    
    return create_success_response(
        data={
            "total_paginas_leidas": total_paginas,
            "total_lecturas": total_lecturas,
            "promedio_paginas_por_lectura": round(promedio_paginas, 2),
            "usuario_id": current_user.idUsuario,
            "usuario_nombre": current_user.nombre
        },
        message=f"Total de páginas leídas: {total_paginas}",
        count=1
    )
