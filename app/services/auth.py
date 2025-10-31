from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.usuario import Usuario
from app.schemas.usuario import TokenData
from app.utils.security import verify_password, verify_token
from app.utils.responses import create_error_response, ErrorCodes
from app.database import get_db
from typing import Optional

security = HTTPBearer()


def authenticate_user(db: Session, email: str, password: str) -> Optional[Usuario]:
    """
    Autentica un usuario verificando email y contraseña.
    Retorna el usuario si las credenciales son correctas, None si no.
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None
    if not verify_password(password, usuario.password):
        return None
    return usuario


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtiene el usuario actual desde el token JWT.
    Se usa como dependencia en los endpoints protegidos.
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=create_error_response(
            ErrorCodes.TOKEN_INVALID,
            "No se pudo validar las credenciales"
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                ErrorCodes.TOKEN_EXPIRED,
                "El token ha expirado o es inválido"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                ErrorCodes.USER_NOT_FOUND,
                "Usuario no encontrado"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return usuario


async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Verifica que el usuario actual esté activo.
    """
    from app.models.usuario import EstadoUsuario
    if current_user.estado != EstadoUsuario.ACTIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=create_error_response(
                ErrorCodes.USER_INACTIVE,
                "El usuario está inactivo o suspendido"
            )
        )
    return current_user
