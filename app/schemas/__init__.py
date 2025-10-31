# Exportar todos los schemas para fácil importación
from app.schemas.usuario import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioLogin,
    Token,
    TokenData
)
from app.schemas.libro import (
    LibroBase,
    LibroCreate,
    LibroUpdate,
    LibroResponse,
    EditorialCreate,
    EditorialResponse,
    AutorCreate,
    AutorResponse
)
from app.schemas.lectura import (
    LecturaBase,
    LecturaCreate,
    LecturaUpdate,
    LecturaResponse,
    LecturaDetailResponse
)
from app.schemas.preferencia import (
    PreferenciaCreate,
    PreferenciaUpdate,
    PreferenciaResponse,
    LenguajeCreate,
    LenguajeResponse,
    CategoriaCreate,
    CategoriaResponse
)
from app.schemas.nivel import (
    NivelCreate,
    NivelResponse
)

__all__ = [
    # Usuario
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "UsuarioLogin",
    "Token",
    "TokenData",
    # Libro
    "LibroBase",
    "LibroCreate",
    "LibroUpdate",
    "LibroResponse",
    "EditorialCreate",
    "EditorialResponse",
    "AutorCreate",
    "AutorResponse",
    # Lectura
    "LecturaBase",
    "LecturaCreate",
    "LecturaUpdate",
    "LecturaResponse",
    "LecturaDetailResponse",
    # Preferencia
    "PreferenciaCreate",
    "PreferenciaUpdate",
    "PreferenciaResponse",
    "LenguajeCreate",
    "LenguajeResponse",
    "CategoriaCreate",
    "CategoriaResponse",
    # Nivel
    "NivelCreate",
    "NivelResponse",
]
