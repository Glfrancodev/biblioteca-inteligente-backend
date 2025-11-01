from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.database import get_db
from app.models.usuario import Usuario, EstadoUsuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioLogin,
    Token
)
from app.utils.security import get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.auth import authenticate_user, get_current_active_user
from app.utils.responses import create_success_response, create_error_response, ErrorCodes

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    # Verificar si el email ya existe
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                ErrorCodes.EMAIL_ALREADY_EXISTS,
                "El email ya está registrado"
            )
        )
    
    # Verificar si el registro ya existe
    db_usuario = db.query(Usuario).filter(Usuario.registro == usuario.registro).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                ErrorCodes.REGISTRO_ALREADY_EXISTS,
                "El registro ya está en uso"
            )
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(usuario.password)
    db_usuario = Usuario(
        registro=usuario.registro,
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        password=hashed_password,
        estado=EstadoUsuario.ACTIVO
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    # Convertir a dict para la respuesta
    usuario_dict = UsuarioResponse.model_validate(db_usuario).model_dump()
    
    return create_success_response(
        data=usuario_dict,
        message="Usuario registrado exitosamente"
    )


@auth_router.post("/login")
def login(
    login_data: UsuarioLogin,
    db: Session = Depends(get_db)
):
    """Iniciar sesión y obtener token de acceso"""
    usuario = authenticate_user(db, login_data.email, login_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                ErrorCodes.INVALID_CREDENTIALS,
                "Email o contraseña incorrectos"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )
    
    return create_success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # en segundos
        },
        message="Inicio de sesión exitoso"
    )


@router.get("/me")
def read_users_me(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener información del usuario actual"""
    usuario_dict = UsuarioResponse.model_validate(current_user).model_dump()
    return create_success_response(
        data=usuario_dict,
        message="Usuario obtenido exitosamente",
        count=1
    )


@router.get("")
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener lista de usuarios"""
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    usuarios_dict = [UsuarioResponse.model_validate(u).model_dump() for u in usuarios]
    
    # Obtener total para paginación
    total = db.query(Usuario).count()
    
    return create_success_response(
        data=usuarios_dict,
        message="Usuarios obtenidos exitosamente",
        count=len(usuarios_dict)
    )


@router.get("/{usuario_id}")
def read_user(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener un usuario por ID"""
    usuario = db.query(Usuario).filter(Usuario.idUsuario == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.USER_NOT_FOUND,
                "Usuario no encontrado"
            )
        )
    
    usuario_dict = UsuarioResponse.model_validate(usuario).model_dump()
    return create_success_response(
        data=usuario_dict,
        message="Usuario obtenido exitosamente",
        count=1
    )


@router.put("/{usuario_id}")
def update_user(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Actualizar información de un usuario"""
    # Verificar que el usuario solo pueda actualizar su propia información
    if current_user.idUsuario != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=create_error_response(
                ErrorCodes.INSUFFICIENT_PERMISSIONS,
                "No tienes permiso para actualizar este usuario"
            )
        )
    
    db_usuario = db.query(Usuario).filter(Usuario.idUsuario == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.USER_NOT_FOUND,
                "Usuario no encontrado"
            )
        )
    
    # Actualizar campos
    update_data = usuario_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
    
    db.commit()
    db.refresh(db_usuario)
    
    usuario_dict = UsuarioResponse.model_validate(db_usuario).model_dump()
    return create_success_response(
        data=usuario_dict,
        message="Usuario actualizado exitosamente"
    )


@router.delete("/{usuario_id}")
def delete_user(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Eliminar un usuario"""
    # Verificar que el usuario solo pueda eliminar su propia cuenta
    if current_user.idUsuario != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=create_error_response(
                ErrorCodes.INSUFFICIENT_PERMISSIONS,
                "No tienes permiso para eliminar este usuario"
            )
        )
    
    db_usuario = db.query(Usuario).filter(Usuario.idUsuario == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                ErrorCodes.USER_NOT_FOUND,
                "Usuario no encontrado"
            )
        )
    
    db.delete(db_usuario)
    db.commit()
    
    return create_success_response(
        data={"deleted": True, "id": usuario_id},
        message="Usuario eliminado exitosamente"
    )
