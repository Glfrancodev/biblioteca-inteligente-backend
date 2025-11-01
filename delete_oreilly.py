"""Script para borrar libros de O'Reilly de la base de datos"""
from app.database.session import SessionLocal
from app.models.libro import Libro, Editorial

db = SessionLocal()

try:
    # Buscar editorial O'Reilly
    editorial = db.query(Editorial).filter(Editorial.nombre == "O'Reilly Media").first()
    
    if editorial:
        # Buscar libros de esa editorial
        libros = db.query(Libro).filter(Libro.idEditorial == editorial.idEditorial).all()
        
        print(f"Encontrados {len(libros)} libros de O'Reilly Media")
        
        for libro in libros:
            print(f"  Eliminando: {libro.titulo}")
            db.delete(libro)
        
        db.commit()
        print(f"\n✓ {len(libros)} libros eliminados correctamente")
    else:
        print("No se encontró la editorial O'Reilly Media")
        
except Exception as e:
    print(f"Error: {str(e)}")
    db.rollback()
finally:
    db.close()
