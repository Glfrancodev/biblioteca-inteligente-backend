from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.utils.responses import ErrorCodes
import traceback


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Manejador personalizado para HTTPException.
    Convierte las excepciones HTTP en formato estándar.
    """
    # Si el detail ya es un dict con el formato estándar, devolverlo directamente
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # Mapear códigos HTTP a códigos de error
    error_code_map = {
        401: ErrorCodes.UNAUTHORIZED,
        403: ErrorCodes.INSUFFICIENT_PERMISSIONS,
        404: ErrorCodes.NOT_FOUND,
        500: ErrorCodes.INTERNAL_ERROR,
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCodes.INTERNAL_ERROR)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": str(exc.detail),
                "details": None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador para errores de validación de Pydantic (422).
    Formatea los errores de validación en el formato estándar.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": ErrorCodes.VALIDATION_ERROR,
                "message": "Error de validación en los datos proporcionados",
                "details": errors
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Manejador para errores de SQLAlchemy (base de datos).
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": ErrorCodes.DATABASE_ERROR,
                "message": "Error en la base de datos",
                "details": str(exc) if request.app.debug else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejador general para cualquier excepción no capturada.
    """
    # Registrar el error completo en logs (en producción usar logging)
    print(f"Error no manejado: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": ErrorCodes.INTERNAL_ERROR,
                "message": "Error interno del servidor",
                "details": str(exc) if request.app.debug else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def setup_exception_handlers(app):
    """
    Configura todos los manejadores de excepciones en la aplicación.
    Llamar esta función en main.py después de crear la app.
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
