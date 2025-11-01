from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base


class Editorial(Base):
    __tablename__ = "editoriales"

    idEditorial = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, unique=True)

    # Relaciones
    libros = relationship("Libro", back_populates="editorial")

    def __repr__(self):
        return f"<Editorial(id={self.idEditorial}, nombre={self.nombre})>"


class Autor(Base):
    __tablename__ = "autores"

    idAutor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)

    # Relaciones
    autor_libros = relationship("AutorLibro", back_populates="autor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Autor(id={self.idAutor}, nombre={self.nombre})>"


class Libro(Base):
    __tablename__ = "libros"

    idLibro = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(300), nullable=False, index=True)
    totalPaginas = Column(Integer, nullable=False)
    sinopsis = Column(String(2000), nullable=True)
    urlLibro = Column(String(500), nullable=True)
    urlPortada = Column(String(500), nullable=True)
    idEditorial = Column(Integer, ForeignKey("editoriales.idEditorial"), nullable=False)

    # Relaciones
    editorial = relationship("Editorial", back_populates="libros")
    autor_libros = relationship("AutorLibro", back_populates="libro", cascade="all, delete-orphan")
    lecturas = relationship("Lectura", back_populates="libro", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Libro(id={self.idLibro}, titulo={self.titulo})>"


class AutorLibro(Base):
    __tablename__ = "autor_libros"

    idAutorLibro = Column(Integer, primary_key=True, index=True)
    idAutor = Column(Integer, ForeignKey("autores.idAutor"), nullable=False)
    idLibro = Column(Integer, ForeignKey("libros.idLibro"), nullable=False)

    # Relaciones
    autor = relationship("Autor", back_populates="autor_libros")
    libro = relationship("Libro", back_populates="autor_libros")

    def __repr__(self):
        return f"<AutorLibro(id={self.idAutorLibro}, autor_id={self.idAutor}, libro_id={self.idLibro})>"
