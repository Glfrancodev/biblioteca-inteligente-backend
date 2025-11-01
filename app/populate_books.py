"""
Script para poblar la base de datos con libros desde Google Books API
Categoriza los libros según lenguajes y categorías existentes
Ejecutar: python -m app.populate_books
"""
import sys
from pathlib import Path
import re
from typing import List, Dict, Optional

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.libro import Libro, Autor, Editorial, AutorLibro, LibroCategoria, LibroLenguaje
from app.models.preferencia import Lenguaje, Categoria
from app.services.google_books_service import GoogleBooksService


class BookPopulator:
    """Clase para poblar libros categorizados"""
    
    def __init__(self):
        self.google_books = GoogleBooksService()
        
        # Mapeo de categorías de Google Books a nuestras categorías
        self.category_mapping = {
            # Lenguajes de programación
            "python": ["Python"],
            "javascript": ["JavaScript"],  
            "java programming": ["Java"],
            "c++ programming": ["C++"],
            "c# programming": ["C#"],
            "typescript": ["TypeScript"],
            "golang": ["Go"],
            "rust programming": ["Rust"],
            "php programming": ["PHP"],
            "ruby programming": ["Ruby"],
            "swift programming": ["Swift"],
            "kotlin programming": ["Kotlin"],
            
            # Categorías temáticas
            "algorithms": ["Algoritmos y Estructuras de Datos"],
            "data structures": ["Algoritmos y Estructuras de Datos"],
            "web development": ["Desarrollo Web"],
            "react programming": ["Desarrollo Web"],
            "angular programming": ["Desarrollo Web"],
            "node.js programming": ["Desarrollo Web"],
            "mobile development": ["Desarrollo Móvil"],
            "artificial intelligence": ["Inteligencia Artificial"],
            "machine learning": ["Machine Learning"],
            "database": ["Bases de Datos"],
            "cybersecurity": ["Seguridad Informática"],
            "devops": ["DevOps"],
            "cloud computing": ["Cloud Computing"],
            "software engineering": ["Arquitectura de Software"],
            "architecture": ["Arquitectura de Software"],
        }
        
        # Mapeo de palabras clave a lenguajes/categorías
        self.keyword_mapping = {
            # Lenguajes
            "python": "Python",
            "javascript": "JavaScript", 
            "java": "Java",
            "c++": "C++",
            "c#": "C#",
            "typescript": "TypeScript",
            "go": "Go",
            "golang": "Go",
            "rust": "Rust",
            "php": "PHP",
            "ruby": "Ruby",
            "swift": "Swift",
            "kotlin": "Kotlin",
            
            # Categorías por palabras clave
            "algorithm": "Algoritmos y Estructuras de Datos",
            "data structure": "Algoritmos y Estructuras de Datos",
            "web": "Desarrollo Web",
            "react": "Desarrollo Web",
            "angular": "Desarrollo Web",
            "vue": "Desarrollo Web",
            "html": "Desarrollo Web",
            "css": "Desarrollo Web",
            "mobile": "Desarrollo Móvil",
            "android": "Desarrollo Móvil",
            "ios": "Desarrollo Móvil",
            "ai": "Inteligencia Artificial",
            "artificial intelligence": "Inteligencia Artificial",
            "machine learning": "Machine Learning",
            "ml": "Machine Learning",
            "database": "Bases de Datos",
            "sql": "Bases de Datos",
            "mysql": "Bases de Datos",
            "postgresql": "Bases de Datos",
            "security": "Seguridad Informática",
            "cybersecurity": "Seguridad Informática",
            "devops": "DevOps",
            "docker": "DevOps",
            "kubernetes": "DevOps",
            "cloud": "Cloud Computing",
            "aws": "Cloud Computing",
            "azure": "Cloud Computing",
            "architecture": "Arquitectura de Software",
            "design pattern": "Arquitectura de Software",
        }
    
    def categorize_book(self, book_metadata: Dict, db: Session) -> Dict:
        """
        Categoriza un libro y asigna lenguajes y categorías
        """
        titulo = book_metadata.get("titulo", "").lower()
        sinopsis = book_metadata.get("sinopsis", "").lower()
        categorias_google = book_metadata.get("categorias", [])
        
        # Texto completo para análisis
        texto_completo = f"{titulo} {sinopsis} {' '.join(categorias_google)}".lower()
        
        # Buscar lenguajes relacionados
        lenguajes_encontrados = set()
        categorias_encontradas = set()
        
        # Buscar por palabras clave en el texto
        for keyword, mapped_value in self.keyword_mapping.items():
            if keyword.lower() in texto_completo:
                # Verificar si es un lenguaje o categoría
                lenguaje = db.query(Lenguaje).filter(Lenguaje.nombre == mapped_value).first()
                if lenguaje:
                    lenguajes_encontrados.add(mapped_value)
                else:
                    categoria = db.query(Categoria).filter(Categoria.nombre == mapped_value).first()
                    if categoria:
                        categorias_encontradas.add(mapped_value)
        
        # Si no encontramos categorías, asignar una por defecto basada en el contexto
        if not categorias_encontradas and not lenguajes_encontrados:
            # Análisis más general
            if any(word in texto_completo for word in ["programming", "code", "software", "development"]):
                categorias_encontradas.add("Arquitectura de Software")
            elif any(word in texto_completo for word in ["mathematics", "math", "algebra", "calculus"]):
                # No tenemos categoría de matemáticas, asignar a algoritmos
                categorias_encontradas.add("Algoritmos y Estructuras de Datos")
            elif any(word in texto_completo for word in ["business", "management", "administration"]):
                # Para libros de negocio, asignar a arquitectura (gestión de proyectos)
                categorias_encontradas.add("Arquitectura de Software")
        
        return {
            "lenguajes": list(lenguajes_encontrados),
            "categorias": list(categorias_encontradas),
            "metadata": book_metadata
        }
    
    def create_or_get_editorial(self, nombre_editorial: str, db: Session) -> Editorial:
        """Crea o obtiene una editorial"""
        editorial = db.query(Editorial).filter(Editorial.nombre == nombre_editorial).first()
        if not editorial:
            editorial = Editorial(nombre=nombre_editorial)
            db.add(editorial)
            db.flush()  # Para obtener el ID
        return editorial
    
    def create_or_get_autor(self, nombre_autor: str, db: Session) -> Autor:
        """Crea o obtiene un autor"""
        autor = db.query(Autor).filter(Autor.nombre == nombre_autor).first()
        if not autor:
            autor = Autor(nombre=nombre_autor)
            db.add(autor)
            db.flush()  # Para obtener el ID
        return autor
    
    def save_book_to_db(self, categorized_book: Dict, db: Session) -> Optional[Libro]:
        """Guarda un libro categorizado en la base de datos"""
        try:
            metadata = categorized_book["metadata"]
            lenguajes_nombres = categorized_book["lenguajes"]
            categorias_nombres = categorized_book["categorias"]
            
            # Verificar si el libro ya existe (por título)
            existing_book = db.query(Libro).filter(Libro.titulo == metadata["titulo"]).first()
            if existing_book:
                print(f"  Libro ya existe: {metadata['titulo']}")
                return existing_book
            
            # Crear o obtener editorial
            editorial = self.create_or_get_editorial(metadata["editorial"], db)
            
            # Crear libro (Google Books no tiene PDF, solo infoLink)
            libro = Libro(
                titulo=metadata["titulo"],
                totalPaginas=metadata["paginas_totales"],
                sinopsis=metadata["sinopsis"],
                urlPortada=metadata["portada_url"],
                urlLibro=None,  # Google Books no proporciona PDF
                idEditorial=editorial.idEditorial
            )
            
            db.add(libro)
            db.flush()  # Para obtener el ID del libro
            
            # Agregar autores
            for nombre_autor in metadata["autores"]:
                autor = self.create_or_get_autor(nombre_autor, db)
                autor_libro = AutorLibro(
                    idAutor=autor.idAutor,
                    idLibro=libro.idLibro
                )
                db.add(autor_libro)
            
            # AGREGAR CATEGORÍAS
            for cat_nombre in categorias_nombres:
                categoria = db.query(Categoria).filter(Categoria.nombre == cat_nombre).first()
                if categoria:
                    libro_cat = LibroCategoria(
                        idLibro=libro.idLibro,
                        idCategoria=categoria.idCategoria
                    )
                    db.add(libro_cat)
            
            # AGREGAR LENGUAJES
            for lang_nombre in lenguajes_nombres:
                lenguaje = db.query(Lenguaje).filter(Lenguaje.nombre == lang_nombre).first()
                if lenguaje:
                    libro_lang = LibroLenguaje(
                        idLibro=libro.idLibro,
                        idLenguaje=lenguaje.idLenguaje
                    )
                    db.add(libro_lang)
            
            return libro
            
        except Exception as e:
            print(f"Error al guardar libro {metadata.get('titulo', 'Sin título')}: {str(e)}")
            return None
    
    def populate_books(self, total_books: int = 500):
        """Función principal para poblar libros"""
        print(f"Iniciando población de {total_books} libros categorizados...\n")
        
        db = SessionLocal()
        
        try:
            # Verificar que existan lenguajes y categorías
            lenguajes_count = db.query(Lenguaje).count()
            categorias_count = db.query(Categoria).count()
            
            print(f"Lenguajes disponibles: {lenguajes_count}")
            print(f"Categorías disponibles: {categorias_count}")
            
            if lenguajes_count == 0 or categorias_count == 0:
                print("Debes ejecutar primero el seed_data para tener lenguajes y categorías")
                return
            
            # Obtener libros de Google Books
            print("\nObteniendo libros desde Google Books API...")
            raw_books = self.google_books.get_programming_books(total_books=total_books)
            
            if not raw_books:
                print("No se obtuvieron libros de Google Books")
                return
            
            print(f"Obtenidos {len(raw_books)} libros desde Google Books")
            
            # Procesar y categorizar libros
            print("\nCategorizando y guardando libros...")
            saved_count = 0
            skipped_count = 0
            
            for i, book_metadata in enumerate(raw_books, 1):
                print(f"\nProcesando libro {i}/{len(raw_books)}: {book_metadata.get('titulo', 'Sin título')}")
                
                # Categorizar libro
                categorized_book = self.categorize_book(book_metadata, db)
                
                # Mostrar categorización
                lenguajes = categorized_book["lenguajes"]
                categorias = categorized_book["categorias"]
                print(f"  Lenguajes: {lenguajes if lenguajes else 'Ninguno'}")
                print(f"  Categorías: {categorias if categorias else 'Ninguna'}")
                
                # Guardar en base de datos
                saved_book = self.save_book_to_db(categorized_book, db)
                
                if saved_book:
                    saved_count += 1
                    print(f"  Guardado: {saved_book.titulo}")
                else:
                    skipped_count += 1
                    print(f"  Omitido")
                
                # Commit cada 10 libros para evitar transacciones muy largas
                if i % 10 == 0:
                    db.commit()
                    print(f"  Guardados {saved_count} libros hasta ahora...")
            
            # Commit final
            db.commit()
            
            print(f"\nPoblación completada!")
            print(f"Libros guardados: {saved_count}")
            print(f"Libros omitidos: {skipped_count}")
            print(f"Total procesados: {len(raw_books)}")
            
        except Exception as e:
            print(f"\nError durante la población: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()


# Esta función se llamará desde la API, no directamente
# No necesitamos main() para ejecución desde terminal