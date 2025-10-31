from pydantic import BaseModel, Field, ConfigDict


# Schemas para Nivel
class NivelBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)


class NivelCreate(NivelBase):
    pass


class NivelResponse(NivelBase):
    idNivel: int

    model_config = ConfigDict(from_attributes=True)
