from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from app.models.lectura import EstadoLectura


# Schemas para Lectura
class LecturaBase(BaseModel):
    paginaLeidas: int = Field(default=0, ge=0)
    estado: EstadoLectura = EstadoLectura.NO_INICIADO


class LecturaCreate(LecturaBase):
    idLibro: int


class LecturaUpdate(BaseModel):
    paginaLeidas: Optional[int] = Field(None, ge=0)
    estado: Optional[EstadoLectura] = None


class LecturaResponse(LecturaBase):
    idLectura: int
    idUsuario: int
    idLibro: int

    model_config = ConfigDict(from_attributes=True)


class LecturaDetailResponse(LecturaResponse):
    libro_titulo: Optional[str] = None
    libro_total_paginas: Optional[int] = None
    progreso_porcentaje: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
