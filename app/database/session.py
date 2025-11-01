from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base
from app.models.usuario import Usuario
from app.models.libro import Libro, Autor, Editorial, AutorLibro, LibroCategoria, LibroLenguaje
from app.models.lectura import Lectura
from app.models.preferencia import Preferencia, Lenguaje, Categoria, PreferenciaLenguaje, PreferenciaCategoria
from app.models.nivel import Nivel
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener configuración de la base de datos desde variables de entorno
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bookapp")

# Construir la URL de la base de datos
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear el engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Muestra las consultas SQL en la consola (solo para desarrollo)
    pool_pre_ping=True  # Verifica la conexión antes de usar
)

# Crear la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia para obtener la sesión de base de datos.
    Se usa en los endpoints de FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crea todas las tablas en la base de datos.
    Solo se debe usar en desarrollo o para inicialización.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Elimina todas las tablas de la base de datos.
    ¡USAR CON PRECAUCIÓN!
    """
    Base.metadata.drop_all(bind=engine)
