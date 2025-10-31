# Exportar todos los routers
from app.routes.usuarios import router as usuarios_router, auth_router
from app.routes.libros import router as libros_router, editorial_router, autor_router
from app.routes.lecturas import router as lecturas_router
from app.routes.preferencias import router as preferencias_router, lenguaje_router, categoria_router

__all__ = [
    "usuarios_router",
    "auth_router",
    "libros_router",
    "editorial_router",
    "autor_router",
    "lecturas_router",
    "preferencias_router",
    "lenguaje_router",
    "categoria_router",
]
