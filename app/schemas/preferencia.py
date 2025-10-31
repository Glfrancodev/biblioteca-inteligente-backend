from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.schemas.nivel import NivelResponse


# Schemas para Lenguaje
class LenguajeBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)


class LenguajeCreate(LenguajeBase):
    pass


class LenguajeResponse(LenguajeBase):
    idLenguaje: int

    model_config = ConfigDict(from_attributes=True)


# Schemas para Categoria
class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaResponse(CategoriaBase):
    idCategoria: int

    model_config = ConfigDict(from_attributes=True)


# Schemas para Preferencia
class PreferenciaCreate(BaseModel):
    lenguajes_ids: List[int] = Field(default_factory=list)
    categorias_ids: List[int] = Field(default_factory=list)
    nivel_id: Optional[int] = None


class PreferenciaUpdate(BaseModel):
    lenguajes_ids: Optional[List[int]] = None
    categorias_ids: Optional[List[int]] = None
    nivel_id: Optional[int] = None


class PreferenciaResponse(BaseModel):
    idPreferencias: int
    idUsuario: int
    idNivel: Optional[int] = None
    creada_en: datetime
    lenguajes: List[LenguajeResponse] = []
    categorias: List[CategoriaResponse] = []
    nivel: Optional[NivelResponse] = None

    model_config = ConfigDict(from_attributes=True)
