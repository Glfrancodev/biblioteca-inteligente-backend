from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any
from datetime import datetime

# TypeVar para hacer responses genéricos
T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    """
    Respuesta estándar para todas las peticiones exitosas.
    Envuelve los datos en un formato consistente.
    """
    success: bool = True
    data: T
    message: str = "Operación exitosa"
    timestamp: datetime = datetime.utcnow()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorDetail(BaseModel):
    """Detalle del error"""
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    """
    Respuesta estándar para todos los errores.
    """
    success: bool = False
    error: ErrorDetail
    timestamp: datetime = datetime.utcnow()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta paginada estándar.
    """
    success: bool = True
    data: list[T]
    pagination: dict = {
        "total": 0,
        "page": 1,
        "page_size": 100,
        "has_more": False
    }
    message: str = "Operación exitosa"
    timestamp: datetime = datetime.utcnow()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Códigos de error estandarizados
class ErrorCodes:
    """Códigos de error consistentes para toda la aplicación"""
    
    # Autenticación (1000-1099)
    INVALID_CREDENTIALS = "AUTH_001"
    TOKEN_EXPIRED = "AUTH_002"
    TOKEN_INVALID = "AUTH_003"
    UNAUTHORIZED = "AUTH_004"
    INSUFFICIENT_PERMISSIONS = "AUTH_005"
    
    # Usuarios (1100-1199)
    USER_NOT_FOUND = "USER_001"
    USER_ALREADY_EXISTS = "USER_002"
    EMAIL_ALREADY_EXISTS = "USER_003"
    REGISTRO_ALREADY_EXISTS = "USER_004"
    USER_INACTIVE = "USER_005"
    
    # Libros (1200-1299)
    BOOK_NOT_FOUND = "BOOK_001"
    EDITORIAL_NOT_FOUND = "BOOK_002"
    AUTHOR_NOT_FOUND = "BOOK_003"
    FILE_NOT_FOUND = "BOOK_004"
    S3_ERROR = "BOOK_005"
    
    # Lecturas (1300-1399)
    READING_NOT_FOUND = "READING_001"
    READING_ALREADY_EXISTS = "READING_002"
    PAGES_EXCEED_TOTAL = "READING_003"
    
    # Preferencias (1400-1499)
    PREFERENCE_NOT_FOUND = "PREF_001"
    PREFERENCE_ALREADY_EXISTS = "PREF_002"
    LANGUAGE_NOT_FOUND = "PREF_003"
    CATEGORY_NOT_FOUND = "PREF_004"
    
    # Validación (9000-9099)
    VALIDATION_ERROR = "VAL_001"
    INVALID_INPUT = "VAL_002"
    
    # Sistema (9900-9999)
    INTERNAL_ERROR = "SYS_001"
    DATABASE_ERROR = "SYS_002"
    NOT_FOUND = "SYS_003"


def create_success_response(
    data: Any,
    message: str = "Operación exitosa",
    count: Optional[int] = None
) -> dict:
    """
    Helper para crear respuestas exitosas de forma sencilla.
    
    Args:
        data: Datos de la respuesta
        message: Mensaje descriptivo
        count: Cantidad de elementos (opcional, para listas)
    
    Ejemplo:
        return create_success_response(
            data=usuarios, 
            message="Usuarios obtenidos exitosamente",
            count=len(usuarios)
        )
    """
    response = {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Añadir count solo si se proporciona
    if count is not None:
        response["count"] = count
    
    return response


def create_error_response(
    code: str,
    message: str,
    details: Optional[Any] = None
) -> dict:
    """
    Helper para crear respuestas de error de forma sencilla.
    
    Ejemplo:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(
                ErrorCodes.USER_NOT_FOUND,
                "Usuario no encontrado"
            )
        )
    """
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details
        },
        "timestamp": datetime.utcnow().isoformat()
    }


def create_paginated_response(
    data: list,
    total: int,
    page: int = 1,
    page_size: int = 100,
    message: str = "Operación exitosa"
) -> dict:
    """
    Helper para crear respuestas paginadas.
    
    Ejemplo:
        return create_paginated_response(
            usuarios,
            total=len(usuarios),
            page=1,
            page_size=100
        )
    """
    return {
        "success": True,
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": total > (page * page_size)
        },
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
