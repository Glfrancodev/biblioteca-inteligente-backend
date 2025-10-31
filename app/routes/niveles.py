from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.usuario import Usuario
from app.models.nivel import Nivel
from app.schemas.nivel import (
    NivelCreate,
    NivelResponse
)
from app.services.auth import get_current_active_user
from app.utils.responses import create_success_response, create_error_response, ErrorCodes

router = APIRouter(prefix="/niveles", tags=["Niveles"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_nivel(
    nivel: NivelCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo nivel"""
    # Verificar si ya existe un nivel con ese nombre
    nivel_existente = db.query(Nivel).filter(Nivel.nombre == nivel.nombre).first()
    if nivel_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                ErrorCodes.DUPLICATE_ENTRY,
                f"Ya existe un nivel con el nombre '{nivel.nombre}'"
            )
        )
    
    db_nivel = Nivel(nombre=nivel.nombre)
    db.add(db_nivel)
    db.commit()
    db.refresh(db_nivel)
    
    nivel_dict = NivelResponse.model_validate(db_nivel).model_dump()
    return create_success_response(
        data=nivel_dict,
        message="Nivel creado exitosamente"
    )


@router.get("")
def read_niveles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de niveles disponibles"""
    niveles = db.query(Nivel).offset(skip).limit(limit).all()
    niveles_dict = [NivelResponse.model_validate(n).model_dump() for n in niveles]
    
    return create_success_response(
        data=niveles_dict,
        message=f"{len(niveles_dict)} niveles obtenidos exitosamente"
    )


@router.get("/{nivel_id}")
def read_nivel(
    nivel_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un nivel por ID"""
    nivel = db.query(Nivel).filter(Nivel.idNivel == nivel_id).first()
    
    if not nivel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.NOT_FOUND,
                f"Nivel con ID {nivel_id} no encontrado"
            )
        )
    
    nivel_dict = NivelResponse.model_validate(nivel).model_dump()
    return create_success_response(
        data=nivel_dict,
        message="Nivel obtenido exitosamente"
    )


@router.put("/{nivel_id}")
def update_nivel(
    nivel_id: int,
    nivel: NivelCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Actualizar un nivel existente"""
    db_nivel = db.query(Nivel).filter(Nivel.idNivel == nivel_id).first()
    
    if not db_nivel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.NOT_FOUND,
                f"Nivel con ID {nivel_id} no encontrado"
            )
        )
    
    # Verificar si otro nivel ya tiene ese nombre
    nivel_con_mismo_nombre = db.query(Nivel).filter(
        Nivel.nombre == nivel.nombre,
        Nivel.idNivel != nivel_id
    ).first()
    
    if nivel_con_mismo_nombre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                ErrorCodes.DUPLICATE_ENTRY,
                f"Ya existe otro nivel con el nombre '{nivel.nombre}'"
            )
        )
    
    db_nivel.nombre = nivel.nombre
    db.commit()
    db.refresh(db_nivel)
    
    nivel_dict = NivelResponse.model_validate(db_nivel).model_dump()
    return create_success_response(
        data=nivel_dict,
        message="Nivel actualizado exitosamente"
    )


@router.delete("/{nivel_id}")
def delete_nivel(
    nivel_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Eliminar un nivel"""
    db_nivel = db.query(Nivel).filter(Nivel.idNivel == nivel_id).first()
    
    if not db_nivel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.NOT_FOUND,
                f"Nivel con ID {nivel_id} no encontrado"
            )
        )
    
    # Verificar si hay preferencias asociadas
    if db_nivel.preferencias:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                ErrorCodes.CANNOT_DELETE,
                f"No se puede eliminar el nivel porque tiene {len(db_nivel.preferencias)} preferencias asociadas"
            )
        )
    
    db.delete(db_nivel)
    db.commit()
    
    return create_success_response(
        data={"deleted": True},
        message="Nivel eliminado exitosamente"
    )
