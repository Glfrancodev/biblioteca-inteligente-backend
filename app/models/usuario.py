from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base, EstadoUsuario


class Usuario(Base):
    __tablename__ = "usuarios"

    idUsuario = Column(Integer, primary_key=True, index=True)
    registro = Column(String(100), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)
    estado = Column(Enum(EstadoUsuario), default=EstadoUsuario.ACTIVO, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    lecturas = relationship("Lectura", back_populates="usuario", cascade="all, delete-orphan")
    preferencia = relationship("Preferencia", back_populates="usuario", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario(id={self.idUsuario}, registro={self.registro}, nombre={self.nombre})>"
