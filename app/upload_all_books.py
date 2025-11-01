"""
Script para subir múltiples libros organizados por carpetas de autores
- Lee PDFs de carpetas dentro de 'books/'
- Lee portadas (.png) con el mismo nombre que el PDF
- Sube ambos a S3
- Detecta categoría/lenguaje por nombre del archivo
- Usa el nombre de la carpeta como autor
"""
import sys
import os
from pathlib import Path
from typing import Optional, Dict

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.libro import Libro, Autor, Editorial, AutorLibro, LibroCategoria, LibroLenguaje
from app.models.preferencia import Lenguaje, Categoria
from app.services.s3_service import s3_service
import mimetypes


class MultiAuthorBookUploader:
    """Clase para subir libros de múltiples autores"""
    
    def __init__(self):
        # Mapeo de palabras clave a lenguajes
        self.language_keywords = {
            "python": "Python",
            "javascript": "JavaScript",
            "java": "Java",
            "cpp": "C++",
            "c++": "C++",
            "csharp": "C#",
            "c#": "C#",
            "typescript": "TypeScript",
            "go": "Go",
            "golang": "Go",
            "rust": "Rust",
            "php": "PHP",
            "ruby": "Ruby",
            "swift": "Swift",
            "kotlin": "Kotlin",
        }
        
        # Mapeo de palabras clave a categorías
        self.category_keywords = {
            "algorithm": "Algoritmos y Estructuras de Datos",
            "algoritmos": "Algoritmos y Estructuras de Datos",
            "data structure": "Algoritmos y Estructuras de Datos",
            "data-structure": "Algoritmos y Estructuras de Datos",
            "web": "Desarrollo Web",
            "react": "Desarrollo Web",
            "angular": "Desarrollo Web",
            "vue": "Desarrollo Web",
            "desarrollo": "Desarrollo Web",
            "mobile": "Desarrollo Móvil",
            "android": "Desarrollo Móvil",
            "ios": "Desarrollo Móvil",
            "ai": "Inteligencia Artificial",
            "artificial intelligence": "Inteligencia Artificial",
            "machine learning": "Machine Learning",
            "ml": "Machine Learning",
            "database": "Bases de Datos",
            "sql": "Bases de Datos",
            "security": "Seguridad Informática",
            "seguridad": "Seguridad Informática",
            "hacking": "Seguridad Informática",
            "etico": "Seguridad Informática",
            "devops": "DevOps",
            "docker": "DevOps",
            "kubernetes": "DevOps",
            "cloud": "Cloud Computing",
            "aws": "Cloud Computing",
            "azure": "Cloud Computing",
            "architecture": "Arquitectura de Software",
            "design pattern": "Arquitectura de Software",
            "design-pattern": "Arquitectura de Software",
            "scrum": "Arquitectura de Software",
            "agile": "Arquitectura de Software",
        }
    
    def detect_language_and_category(self, filename: str, db: Session) -> Dict:
        """Detecta lenguaje y categoría basándose en el nombre del archivo"""
        filename_lower = filename.lower()
        
        detected_languages = []
        detected_categories = []
        
        # Detectar lenguajes
        for keyword, language in self.language_keywords.items():
            if keyword in filename_lower:
                lenguaje = db.query(Lenguaje).filter(Lenguaje.nombre == language).first()
                if lenguaje and language not in detected_languages:
                    detected_languages.append(language)
        
        # Detectar categorías
        for keyword, category in self.category_keywords.items():
            if keyword in filename_lower:
                categoria = db.query(Categoria).filter(Categoria.nombre == category).first()
                if categoria and category not in detected_categories:
                    detected_categories.append(category)
        
        return {
            "lenguajes": detected_languages,
            "categorias": detected_categories
        }
    
    def find_cover_image(self, pdf_path: str, folder: str) -> Optional[str]:
        """Busca la imagen de portada con el mismo nombre que el PDF"""
        base_name = Path(pdf_path).stem
        
        # Buscar .jpg o .png
        for ext in ['.jpg', '.jpeg', '.png']:
            cover_path = os.path.join(folder, base_name + ext)
            if os.path.exists(cover_path):
                return cover_path
        
        return None
    
    def upload_to_s3(self, file_path: str, s3_key: str) -> Optional[str]:
        """Sube un archivo a S3 y retorna la URL pública"""
        try:
            print(f"    Subiendo a S3: {s3_key}")
            
            # Detectar tipo de contenido
            content_type = mimetypes.guess_type(file_path)[0]
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Leer archivo
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Subir a S3
            s3_service.s3_client.put_object(
                Bucket=s3_service.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ContentDisposition='inline'
            )
            
            # Generar URL pública
            public_url = f"https://{s3_service.bucket_name}.s3.{s3_service.aws_region}.amazonaws.com/{s3_key}"
            
            print(f"    ✓ Subido")
            return public_url
            
        except Exception as e:
            print(f"    ✗ Error al subir a S3: {str(e)}")
            return None
    
    def create_or_get_editorial(self, nombre: str, db: Session) -> Editorial:
        """Crea o obtiene una editorial"""
        editorial = db.query(Editorial).filter(Editorial.nombre == nombre).first()
        if not editorial:
            editorial = Editorial(nombre=nombre)
            db.add(editorial)
            db.flush()
        return editorial
    
    def create_or_get_autor(self, nombre: str, db: Session) -> Autor:
        """Crea o obtiene un autor"""
        autor = db.query(Autor).filter(Autor.nombre == nombre).first()
        if not autor:
            autor = Autor(nombre=nombre)
            db.add(autor)
            db.flush()
        return autor
    
    def process_book(self, pdf_path: str, author_folder: str, author_name: str, db: Session) -> Optional[Libro]:
        """Procesa un libro completo"""
        try:
            filename = os.path.basename(pdf_path)
            book_name = Path(pdf_path).stem
            
            print(f"\n  📖 {filename}")
            
            # 1. Buscar portada
            cover_path = self.find_cover_image(pdf_path, author_folder)
            if not cover_path:
                print(f"    ✗ No se encontró portada")
                return None
            
            print(f"    ✓ Portada: {os.path.basename(cover_path)}")
            
            # 2. Detectar lenguaje y categoría
            detection = self.detect_language_and_category(filename, db)
            if detection['lenguajes']:
                print(f"    Lenguajes: {', '.join(detection['lenguajes'])}")
            if detection['categorias']:
                print(f"    Categorías: {', '.join(detection['categorias'])}")
            
            # 3. Subir portada a S3
            cover_ext = Path(cover_path).suffix
            cover_s3_key = f"portadas/{book_name}_cover{cover_ext}"
            cover_url = self.upload_to_s3(cover_path, cover_s3_key)
            
            # 4. Subir PDF a S3
            pdf_s3_key = f"libros/{filename}"
            pdf_url = self.upload_to_s3(pdf_path, pdf_s3_key)
            
            if not cover_url or not pdf_url:
                print("    ✗ Error al subir archivos")
                return None
            
            # 5. Crear título limpio del nombre del archivo
            titulo = book_name.replace('_', ' ').replace('-', ' ').title()
            
            # 6. Crear o obtener editorial (usar autor como editorial)
            editorial = self.create_or_get_editorial(author_name, db)
            
            # 7. Crear libro en la base de datos
            libro = Libro(
                titulo=titulo,
                totalPaginas=300,  # Valor por defecto
                sinopsis=f"Libro de {author_name} sobre {titulo}",
                urlPortada=cover_url,
                urlLibro=pdf_url,
                idEditorial=editorial.idEditorial
            )
            
            db.add(libro)
            db.flush()
            
            # 8. Agregar autor
            autor = self.create_or_get_autor(author_name, db)
            autor_libro = AutorLibro(
                idAutor=autor.idAutor,
                idLibro=libro.idLibro
            )
            db.add(autor_libro)
            
            # 9. Agregar categorías
            for cat_nombre in detection['categorias']:
                categoria = db.query(Categoria).filter(Categoria.nombre == cat_nombre).first()
                if categoria:
                    libro_cat = LibroCategoria(
                        idLibro=libro.idLibro,
                        idCategoria=categoria.idCategoria
                    )
                    db.add(libro_cat)
            
            # 10. Agregar lenguajes
            for lang_nombre in detection['lenguajes']:
                lenguaje = db.query(Lenguaje).filter(Lenguaje.nombre == lang_nombre).first()
                if lenguaje:
                    libro_lang = LibroLenguaje(
                        idLibro=libro.idLibro,
                        idLenguaje=lenguaje.idLenguaje
                    )
                    db.add(libro_lang)
            
            db.commit()
            print(f"    ✓ Guardado: {libro.titulo}")
            
            return libro
            
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            db.rollback()
            return None
    
    def upload_books_from_folders(self, base_folder: str):
        """Procesa todos los PDFs organizados por carpetas de autores"""
        print(f"Buscando libros en: {base_folder}\n")
        
        if not os.path.exists(base_folder):
            print(f"ERROR: La carpeta {base_folder} no existe")
            return
        
        db = SessionLocal()
        
        try:
            total_success = 0
            total_error = 0
            
            # Recorrer carpetas (cada carpeta es un autor)
            for author_folder in Path(base_folder).iterdir():
                if not author_folder.is_dir():
                    continue
                
                author_name = author_folder.name
                print(f"\n{'='*60}")
                print(f"📚 Autor: {author_name}")
                print(f"{'='*60}")
                
                # Buscar PDFs en esta carpeta
                pdf_files = list(author_folder.glob("*.pdf"))
                
                if not pdf_files:
                    print("  No se encontraron PDFs")
                    continue
                
                print(f"  Encontrados {len(pdf_files)} PDFs")
                
                # Procesar cada libro
                for pdf_path in pdf_files:
                    result = self.process_book(str(pdf_path), str(author_folder), author_name, db)
                    if result:
                        total_success += 1
                    else:
                        total_error += 1
            
            print(f"\n{'='*60}")
            print(f"RESUMEN:")
            print(f"  ✓ Exitosos: {total_success}")
            print(f"  ✗ Errores: {total_error}")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"\nERROR GENERAL: {str(e)}")
            db.rollback()
        finally:
            db.close()


def main():
    """Función principal"""
    books_folder = "books"
    
    uploader = MultiAuthorBookUploader()
    uploader.upload_books_from_folders(books_folder)


if __name__ == "__main__":
    main()
