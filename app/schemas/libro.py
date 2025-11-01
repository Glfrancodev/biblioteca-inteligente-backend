from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List


# Schemas para Editorial
class EditorialBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=200)


class EditorialCreate(EditorialBase):
    pass


class EditorialResponse(EditorialBase):
    idEditorial: int

    model_config = ConfigDict(from_attributes=True)


# Schemas para Autor
class AutorBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=200)


class AutorCreate(AutorBase):
    pass


class AutorResponse(AutorBase):
    idAutor: int

    model_config = ConfigDict(from_attributes=True)


# Schemas para Libro
class LibroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=300)
    totalPaginas: int = Field(..., gt=0)
    sinopsis: Optional[str] = Field(None, max_length=2000)
    urlLibro: Optional[str] = Field(None, max_length=500)
    urlPortada: Optional[str] = Field(None, max_length=500)


class LibroCreate(LibroBase):
    idEditorial: int
    autores_ids: List[int] = Field(..., min_length=1)


class LibroUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=300)
    totalPaginas: Optional[int] = Field(None, gt=0)
    sinopsis: Optional[str] = Field(None, max_length=2000)
    urlLibro: Optional[str] = Field(None, max_length=500)
    urlPortada: Optional[str] = Field(None, max_length=500)
    idEditorial: Optional[int] = None
    autores_ids: Optional[List[int]] = None


class LibroResponse(LibroBase):
    idLibro: int
    idEditorial: int
    editorial: EditorialResponse
    autores: List[AutorResponse] = []

    model_config = ConfigDict(from_attributes=True)
