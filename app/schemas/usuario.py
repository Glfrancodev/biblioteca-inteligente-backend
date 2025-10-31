from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.usuario import EstadoUsuario


# Schemas para Usuario
class UsuarioBase(BaseModel):
    registro: str = Field(..., min_length=3, max_length=100)
    nombre: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6, max_length=100)


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    estado: Optional[EstadoUsuario] = None


class UsuarioResponse(UsuarioBase):
    idUsuario: int
    estado: EstadoUsuario
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
