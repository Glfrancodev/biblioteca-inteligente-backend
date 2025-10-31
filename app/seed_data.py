"""
Script para poblar la base de datos con datos iniciales
Ejecutar: python -m app.seed_data
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.models import Base
from app.models.nivel import Nivel
from app.models.preferencia import Lenguaje, Categoria


def init_db():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas")


def seed_niveles(db: Session):
    """Poblar tabla de niveles"""
    niveles_data = [
        "Principiante",
        "Intermedio",
        "Avanzado",
    ]
    
    existing_niveles = db.query(Nivel).all()
    if existing_niveles:
        print(f"⚠ Ya existen {len(existing_niveles)} niveles en la base de datos")
        return
    
    for nombre in niveles_data:
        nivel = Nivel(nombre=nombre)
        db.add(nivel)
    
    db.commit()
    print(f"✓ {len(niveles_data)} niveles creados")


def seed_lenguajes(db: Session):
    """Poblar tabla de lenguajes"""
    lenguajes_data = [
        "Python",
        "JavaScript",
        "Java",
        "C++",
        "C#",
        "TypeScript",
        "Go",
        "Rust",
        "PHP",
        "Ruby",
        "Swift",
        "Kotlin",
    ]
    
    existing_lenguajes = db.query(Lenguaje).all()
    if existing_lenguajes:
        print(f"⚠ Ya existen {len(existing_lenguajes)} lenguajes en la base de datos")
        return
    
    for nombre in lenguajes_data:
        lenguaje = Lenguaje(nombre=nombre)
        db.add(lenguaje)
    
    db.commit()
    print(f"✓ {len(lenguajes_data)} lenguajes creados")


def seed_categorias(db: Session):
    """Poblar tabla de categorías"""
    categorias_data = [
        "Algoritmos y Estructuras de Datos",
        "Desarrollo Web",
        "Desarrollo Móvil",
        "Inteligencia Artificial",
        "Machine Learning",
        "Bases de Datos",
        "Seguridad Informática",
        "DevOps",
        "Cloud Computing",
        "Arquitectura de Software",
    ]
    
    existing_categorias = db.query(Categoria).all()
    if existing_categorias:
        print(f"⚠ Ya existen {len(existing_categorias)} categorías en la base de datos")
        return
    
    for nombre in categorias_data:
        categoria = Categoria(nombre=nombre)
        db.add(categoria)
    
    db.commit()
    print(f"✓ {len(categorias_data)} categorías creadas")


def main():
    """Función principal para poblar la base de datos"""
    print("🚀 Iniciando seed de base de datos...\n")
    
    # Inicializar base de datos
    init_db()
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Poblar datos
        print("\n📊 Poblando datos iniciales:")
        seed_niveles(db)
        seed_lenguajes(db)
        seed_categorias(db)
        
        print("\n✅ Base de datos poblada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error al poblar la base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
