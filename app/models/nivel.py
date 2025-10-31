from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models import Base


class Nivel(Base):
    __tablename__ = "niveles"

    idNivel = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)

    # Relaciones
    preferencias = relationship("Preferencia", back_populates="nivel")

    def __repr__(self):
        return f"<Nivel(id={self.idNivel}, nombre={self.nombre})>"
