from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base
import enum


class EstadoLectura(str, enum.Enum):
    NO_INICIADO = "no_iniciado"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    ABANDONADO = "abandonado"


class Lectura(Base):
    __tablename__ = "lecturas"

    idLectura = Column(Integer, primary_key=True, index=True)
    paginaLeidas = Column(Integer, default=0, nullable=False)
    estado = Column(Enum(EstadoLectura), default=EstadoLectura.NO_INICIADO, nullable=False)
    idUsuario = Column(Integer, ForeignKey("usuarios.idUsuario"), nullable=False)
    idLibro = Column(Integer, ForeignKey("libros.idLibro"), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="lecturas")
    libro = relationship("Libro", back_populates="lecturas")

    def __repr__(self):
        return f"<Lectura(id={self.idLectura}, usuario_id={self.idUsuario}, libro_id={self.idLibro}, estado={self.estado})>"
