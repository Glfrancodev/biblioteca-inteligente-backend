"""
Script simplificado para subir libros de O'Reilly a la base de datos
- Lee PDFs de la carpeta 'books/'
- Lee portadas de la carpeta 'books/' (mismo nombre que PDF pero .jpg o .png)
- Sube ambos a S3
- Detecta categoría/lenguaje por nombre del archivo
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


class OreillyBookUploader:
    """Clase para subir libros de O'Reilly"""
    
    def __init__(self):
        self.editorial_name = "O'Reilly Media"
        
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
            "data structure": "Algoritmos y Estructuras de Datos",
            "data-structure": "Algoritmos y Estructuras de Datos",
            "web": "Desarrollo Web",
            "react": "Desarrollo Web",
            "angular": "Desarrollo Web",
            "vue": "Desarrollo Web",
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
            "devops": "DevOps",
            "docker": "DevOps",
            "kubernetes": "DevOps",
            "cloud": "Cloud Computing",
            "aws": "Cloud Computing",
            "azure": "Cloud Computing",
            "architecture": "Arquitectura de Software",
            "design pattern": "Arquitectura de Software",
            "design-pattern": "Arquitectura de Software",
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
    
    def find_cover_image(self, pdf_path: str, books_folder: str) -> Optional[str]:
        """Busca la imagen de portada con el mismo nombre que el PDF"""
        base_name = Path(pdf_path).stem
        
        # Buscar .jpg o .png
        for ext in ['.jpg', '.jpeg', '.png']:
            cover_path = os.path.join(books_folder, base_name + ext)
            if os.path.exists(cover_path):
                return cover_path
        
        return None
    
    def upload_to_s3(self, file_path: str, s3_key: str) -> Optional[str]:
        """Sube un archivo a S3 y retorna la URL"""
        try:
            print(f"  Subiendo a S3: {s3_key}")
            
            # Detectar tipo de contenido
            content_type = mimetypes.guess_type(file_path)[0]
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Leer archivo
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Subir a S3 usando el cliente directamente
            s3_service.s3_client.put_object(
                Bucket=s3_service.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ContentDisposition='inline'
            )
            
            # Generar URL firmada
            signed_url = s3_service.generate_presigned_url(s3_key)
            
            print(f"  Subido: {signed_url[:80]}...")
            return signed_url
            
        except Exception as e:
            print(f"  Error al subir a S3: {str(e)}")
            return None
    
    def create_or_get_editorial(self, db: Session) -> Editorial:
        """Crea o obtiene la editorial O'Reilly"""
        editorial = db.query(Editorial).filter(Editorial.nombre == self.editorial_name).first()
        if not editorial:
            editorial = Editorial(nombre=self.editorial_name)
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
    
    def process_book(self, pdf_path: str, books_folder: str, db: Session) -> Optional[Libro]:
        """Procesa un libro completo"""
        try:
            filename = os.path.basename(pdf_path)
            book_name = Path(pdf_path).stem
            
            print(f"\nProcesando: {filename}")
            
            # 1. Buscar portada
            cover_path = self.find_cover_image(pdf_path, books_folder)
            if not cover_path:
                print(f"  ERROR: No se encontró portada para {filename}")
                return None
            
            print(f"  Portada encontrada: {os.path.basename(cover_path)}")
            
            # 2. Detectar lenguaje y categoría
            detection = self.detect_language_and_category(filename, db)
            print(f"  Lenguajes: {detection['lenguajes'] if detection['lenguajes'] else 'Ninguno'}")
            print(f"  Categorías: {detection['categorias'] if detection['categorias'] else 'Ninguna'}")
            
            # 3. Subir portada a S3
            cover_ext = Path(cover_path).suffix
            cover_s3_key = f"portadas/{book_name}_cover{cover_ext}"
            cover_url = self.upload_to_s3(cover_path, cover_s3_key)
            
            # 4. Subir PDF a S3
            pdf_s3_key = f"libros/{filename}"
            pdf_url = self.upload_to_s3(pdf_path, pdf_s3_key)
            
            if not cover_url or not pdf_url:
                print("  ERROR: No se pudieron subir archivos a S3")
                return None
            
            # 5. Crear título limpio del nombre del archivo
            titulo = book_name.replace('_', ' ').replace('-', ' ').title()
            
            # 6. Crear editorial O'Reilly
            editorial = self.create_or_get_editorial(db)
            
            # 7. Crear libro en la base de datos
            libro = Libro(
                titulo=titulo,
                totalPaginas=300,  # Valor por defecto
                sinopsis=f"Libro de O'Reilly Media sobre {titulo}",
                urlPortada=cover_url,
                urlLibro=pdf_url,
                idEditorial=editorial.idEditorial
            )
            
            db.add(libro)
            db.flush()
            
            # 8. Agregar autor
            autor = self.create_or_get_autor("O'Reilly Media", db)
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
            print(f"  GUARDADO: {libro.titulo}")
            
            return libro
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            db.rollback()
            return None
    
    def upload_books_from_folder(self, folder_path: str):
        """Procesa todos los PDFs de una carpeta"""
        print(f"Buscando libros en: {folder_path}\n")
        
        if not os.path.exists(folder_path):
            print(f"ERROR: La carpeta {folder_path} no existe")
            return
        
        # Buscar todos los archivos PDF
        pdf_files = list(Path(folder_path).glob("*.pdf"))
        
        if not pdf_files:
            print("No se encontraron archivos PDF")
            return
        
        print(f"Encontrados {len(pdf_files)} PDFs\n")
        
        db = SessionLocal()
        
        try:
            success_count = 0
            error_count = 0
            
            for pdf_path in pdf_files:
                result = self.process_book(str(pdf_path), folder_path, db)
                if result:
                    success_count += 1
                else:
                    error_count += 1
            
            print(f"\n{'='*50}")
            print(f"COMPLETADO:")
            print(f"  Exitosos: {success_count}")
            print(f"  Errores: {error_count}")
            print(f"{'='*50}")
            
        except Exception as e:
            print(f"\nERROR GENERAL: {str(e)}")
            db.rollback()
        finally:
            db.close()


def main():
    """Función principal"""
    books_folder = "books"
    
    uploader = OreillyBookUploader()
    uploader.upload_books_from_folder(books_folder)


if __name__ == "__main__":
    main()
