"""Script para borrar libros del ID 1 al 33"""
from app.database.session import SessionLocal
from app.models.libro import Libro

db = SessionLocal()

try:
    # Buscar libros del ID 1 al 33
    libros = db.query(Libro).filter(Libro.idLibro.between(100, 100)).all()
    
    print(f"Encontrados {len(libros)} libros del ID 1 al 33\n")
    
    for libro in libros:
        print(f"  Eliminando ID {libro.idLibro}: {libro.titulo}")
        db.delete(libro)
    
    db.commit()
    print(f"\n✓ {len(libros)} libros eliminados correctamente")
    
except Exception as e:
    print(f"Error: {str(e)}")
    db.rollback()
finally:
    db.close()
