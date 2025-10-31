from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.usuario import Usuario
from app.models.preferencia import (
    Preferencia,
    Lenguaje,
    Categoria,
    PreferenciaLenguaje,
    PreferenciaCategoria
)
from app.models.nivel import Nivel
from app.schemas.preferencia import (
    PreferenciaCreate,
    PreferenciaUpdate,
    PreferenciaResponse,
    LenguajeCreate,
    LenguajeResponse,
    CategoriaCreate,
    CategoriaResponse
)
from app.schemas.nivel import NivelResponse
from app.services.auth import get_current_active_user
from app.utils.responses import create_success_response, create_error_response, ErrorCodes

router = APIRouter(prefix="/preferencias", tags=["Preferencias"])
lenguaje_router = APIRouter(prefix="/lenguajes", tags=["Lenguajes"])
categoria_router = APIRouter(prefix="/categorias", tags=["Categorías"])


# ENDPOINTS DE PREFERENCIAS
@router.post("", status_code=status.HTTP_201_CREATED)
def create_preferencia(
    preferencia: PreferenciaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear preferencias para el usuario actual"""
    # Verificar si ya tiene preferencias
    preferencia_existente = db.query(Preferencia).filter(
        Preferencia.idUsuario == current_user.idUsuario
    ).first()
    
    if preferencia_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                ErrorCodes.PREFERENCE_ALREADY_EXISTS,
                "El usuario ya tiene preferencias configuradas. Use PUT para actualizar."
            )
        )
    
    # Verificar que el nivel existe si se proporciona
    if preferencia.nivel_id is not None:
        nivel = db.query(Nivel).filter(Nivel.idNivel == preferencia.nivel_id).first()
        if not nivel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    ErrorCodes.NOT_FOUND,
                    f"Nivel con ID {preferencia.nivel_id} no encontrado"
                )
            )
    
    # Crear preferencia
    db_preferencia = Preferencia(
        idUsuario=current_user.idUsuario,
        idNivel=preferencia.nivel_id
    )
    db.add(db_preferencia)
    db.commit()
    db.refresh(db_preferencia)
    
    # Agregar lenguajes
    for lenguaje_id in preferencia.lenguajes_ids:
        lenguaje = db.query(Lenguaje).filter(Lenguaje.idLenguaje == lenguaje_id).first()
        if lenguaje:
            pref_lenguaje = PreferenciaLenguaje(
                idPreferencias=db_preferencia.idPreferencias,
                idLenguaje=lenguaje_id
            )
            db.add(pref_lenguaje)
    
    # Agregar categorías
    for categoria_id in preferencia.categorias_ids:
        categoria = db.query(Categoria).filter(Categoria.idCategoria == categoria_id).first()
        if categoria:
            pref_categoria = PreferenciaCategoria(
                idPreferencias=db_preferencia.idPreferencias,
                idCategoria=categoria_id
            )
            db.add(pref_categoria)
    
    db.commit()
    db.refresh(db_preferencia)
    
    # Construir respuesta
    response = PreferenciaResponse.model_validate(db_preferencia)
    response.lenguajes = [
        LenguajeResponse.model_validate(pl.lenguaje) 
        for pl in db_preferencia.preferencia_lenguajes
    ]
    response.categorias = [
        CategoriaResponse.model_validate(pc.categoria) 
        for pc in db_preferencia.preferencia_categorias
    ]
    if db_preferencia.nivel:
        response.nivel = NivelResponse.model_validate(db_preferencia.nivel)
    
    preferencia_dict = response.model_dump()
    return create_success_response(
        data=preferencia_dict,
        message="Preferencias creadas exitosamente"
    )


@router.get("/me")
def read_my_preferencias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener las preferencias del usuario actual"""
    preferencia = db.query(Preferencia).filter(
        Preferencia.idUsuario == current_user.idUsuario
    ).first()
    
    if not preferencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.PREFERENCE_NOT_FOUND,
                "El usuario no tiene preferencias configuradas"
            )
        )
    
    response = PreferenciaResponse.model_validate(preferencia)
    response.lenguajes = [
        LenguajeResponse.model_validate(pl.lenguaje) 
        for pl in preferencia.preferencia_lenguajes
    ]
    response.categorias = [
        CategoriaResponse.model_validate(pc.categoria) 
        for pc in preferencia.preferencia_categorias
    ]
    if preferencia.nivel:
        response.nivel = NivelResponse.model_validate(preferencia.nivel)
    
    preferencia_dict = response.model_dump()
    return create_success_response(
        data=preferencia_dict,
        message="Preferencias obtenidas exitosamente"
    )


@router.put("/me")
def update_my_preferencias(
    preferencia_update: PreferenciaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Actualizar las preferencias del usuario actual"""
    db_preferencia = db.query(Preferencia).filter(
        Preferencia.idUsuario == current_user.idUsuario
    ).first()
    
    if not db_preferencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.PREFERENCE_NOT_FOUND,
                "El usuario no tiene preferencias configuradas. Use POST para crear."
            )
        )
    
    update_data = preferencia_update.model_dump(exclude_unset=True)
    
    # Actualizar nivel si se proporciona
    if "nivel_id" in update_data:
        if update_data["nivel_id"] is not None:
            nivel = db.query(Nivel).filter(Nivel.idNivel == update_data["nivel_id"]).first()
            if not nivel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=create_error_response(
                        ErrorCodes.NOT_FOUND,
                        f"Nivel con ID {update_data['nivel_id']} no encontrado"
                    )
                )
        db_preferencia.idNivel = update_data["nivel_id"]
    
    # Actualizar lenguajes
    if "lenguajes_ids" in update_data:
        # Eliminar asociaciones existentes
        db.query(PreferenciaLenguaje).filter(
            PreferenciaLenguaje.idPreferencias == db_preferencia.idPreferencias
        ).delete()
        
        # Crear nuevas asociaciones
        for lenguaje_id in update_data["lenguajes_ids"]:
            pref_lenguaje = PreferenciaLenguaje(
                idPreferencias=db_preferencia.idPreferencias,
                idLenguaje=lenguaje_id
            )
            db.add(pref_lenguaje)
    
    # Actualizar categorías
    if "categorias_ids" in update_data:
        # Eliminar asociaciones existentes
        db.query(PreferenciaCategoria).filter(
            PreferenciaCategoria.idPreferencias == db_preferencia.idPreferencias
        ).delete()
        
        # Crear nuevas asociaciones
        for categoria_id in update_data["categorias_ids"]:
            pref_categoria = PreferenciaCategoria(
                idPreferencias=db_preferencia.idPreferencias,
                idCategoria=categoria_id
            )
            db.add(pref_categoria)
    
    db.commit()
    db.refresh(db_preferencia)
    
    response = PreferenciaResponse.model_validate(db_preferencia)
    response.lenguajes = [
        LenguajeResponse.model_validate(pl.lenguaje) 
        for pl in db_preferencia.preferencia_lenguajes
    ]
    response.categorias = [
        CategoriaResponse.model_validate(pc.categoria) 
        for pc in db_preferencia.preferencia_categorias
    ]
    if db_preferencia.nivel:
        response.nivel = NivelResponse.model_validate(db_preferencia.nivel)
    
    preferencia_dict = response.model_dump()
    return create_success_response(
        data=preferencia_dict,
        message="Preferencias actualizadas exitosamente"
    )


@router.delete("/me")
def delete_my_preferencias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Eliminar las preferencias del usuario actual"""
    db_preferencia = db.query(Preferencia).filter(
        Preferencia.idUsuario == current_user.idUsuario
    ).first()
    
    if not db_preferencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.PREFERENCE_NOT_FOUND,
                "El usuario no tiene preferencias configuradas"
            )
        )
    
    db.delete(db_preferencia)
    db.commit()
    
    return create_success_response(
        data={"deleted": True},
        message="Preferencias eliminadas exitosamente"
    )


# ENDPOINTS DE LENGUAJES
@lenguaje_router.post("", status_code=status.HTTP_201_CREATED)
def create_lenguaje(
    lenguaje: LenguajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo lenguaje"""
    db_lenguaje = Lenguaje(nombre=lenguaje.nombre)
    db.add(db_lenguaje)
    db.commit()
    db.refresh(db_lenguaje)
    
    lenguaje_dict = LenguajeResponse.model_validate(db_lenguaje).model_dump()
    return create_success_response(
        data=lenguaje_dict,
        message="Lenguaje creado exitosamente"
    )


@lenguaje_router.get("")
def read_lenguajes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de lenguajes disponibles"""
    lenguajes = db.query(Lenguaje).offset(skip).limit(limit).all()
    lenguajes_dict = [LenguajeResponse.model_validate(l).model_dump() for l in lenguajes]
    
    return create_success_response(
        data=lenguajes_dict,
        message=f"{len(lenguajes_dict)} lenguajes obtenidos exitosamente"
    )


# ENDPOINTS DE CATEGORÍAS
@categoria_router.post("", status_code=status.HTTP_201_CREATED)
def create_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear una nueva categoría"""
    db_categoria = Categoria(nombre=categoria.nombre)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    
    categoria_dict = CategoriaResponse.model_validate(db_categoria).model_dump()
    return create_success_response(
        data=categoria_dict,
        message="Categoría creada exitosamente"
    )


@categoria_router.get("")
def read_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de categorías disponibles"""
    categorias = db.query(Categoria).offset(skip).limit(limit).all()
    categorias_dict = [CategoriaResponse.model_validate(c).model_dump() for c in categorias]
    
    return create_success_response(
        data=categorias_dict,
        message=f"{len(categorias_dict)} categorías obtenidas exitosamente"
    )
