from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base


class Lenguaje(Base):
    __tablename__ = "lenguajes"

    idLenguaje = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)

    # Relaciones
    preferencia_lenguajes = relationship("PreferenciaLenguaje", back_populates="lenguaje", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lenguaje(id={self.idLenguaje}, nombre={self.nombre})>"


class Categoria(Base):
    __tablename__ = "categorias"

    idCategoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)

    # Relaciones
    preferencia_categorias = relationship("PreferenciaCategoria", back_populates="categoria", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Categoria(id={self.idCategoria}, nombre={self.nombre})>"


class Preferencia(Base):
    __tablename__ = "preferencias"

    idPreferencias = Column(Integer, primary_key=True, index=True)
    creada_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    idUsuario = Column(Integer, ForeignKey("usuarios.idUsuario"), nullable=False, unique=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="preferencia")
    preferencia_lenguajes = relationship("PreferenciaLenguaje", back_populates="preferencia", cascade="all, delete-orphan")
    preferencia_categorias = relationship("PreferenciaCategoria", back_populates="preferencia", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Preferencia(id={self.idPreferencias}, usuario_id={self.idUsuario})>"


class PreferenciaLenguaje(Base):
    __tablename__ = "preferencia_lenguajes"

    idPreferenciaLenguaje = Column(Integer, primary_key=True, index=True)
    idPreferencias = Column(Integer, ForeignKey("preferencias.idPreferencias"), nullable=False)
    idLenguaje = Column(Integer, ForeignKey("lenguajes.idLenguaje"), nullable=False)

    # Relaciones
    preferencia = relationship("Preferencia", back_populates="preferencia_lenguajes")
    lenguaje = relationship("Lenguaje", back_populates="preferencia_lenguajes")

    def __repr__(self):
        return f"<PreferenciaLenguaje(id={self.idPreferenciaLenguaje}, pref_id={self.idPreferencias}, len_id={self.idLenguaje})>"


class PreferenciaCategoria(Base):
    __tablename__ = "preferencia_categorias"

    idPreferenciaCategoria = Column(Integer, primary_key=True, index=True)
    idPreferencias = Column(Integer, ForeignKey("preferencias.idPreferencias"), nullable=False)
    idCategoria = Column(Integer, ForeignKey("categorias.idCategoria"), nullable=False)

    # Relaciones
    preferencia = relationship("Preferencia", back_populates="preferencia_categorias")
    categoria = relationship("Categoria", back_populates="preferencia_categorias")

    def __repr__(self):
        return f"<PreferenciaCategoria(id={self.idPreferenciaCategoria}, pref_id={self.idPreferencias}, cat_id={self.idCategoria})>"
