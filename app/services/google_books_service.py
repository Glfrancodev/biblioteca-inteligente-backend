import requests
from typing import List, Dict, Optional
from fastapi import HTTPException
import time


class GoogleBooksService:
    """Servicio para interactuar con Google Books API"""
    
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self):
        self.session = requests.Session()
    
    def search_books(
        self,
        query: str,
        max_results: int = 40,
        start_index: int = 0,
        language: str = "en",
        subject: Optional[str] = None
    ) -> Dict:
        """
        Busca libros en Google Books API
        
        Args:
            query: Término de búsqueda
            max_results: Máximo de resultados por petición (máx: 40)
            start_index: Índice de inicio para paginación
            language: Código de idioma
            subject: Materia/categoría (ej: "programming", "python")
        
        Returns:
            Dict: Respuesta de la API con lista de libros
        """
        try:
            # Construir query
            search_query = query
            if subject:
                search_query = f"subject:{subject}"
            
            params = {
                "q": search_query,
                "maxResults": min(max_results, 40),  # Google limita a 40
                "startIndex": start_index,
                "langRestrict": language
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Log para debugging
            total_items = data.get("totalItems", 0)
            items_count = len(data.get("items", []))
            print(f"  📊 API Response: totalItems={total_items}, items_received={items_count}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error al consultar Google Books API: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al consultar Google Books API: {str(e)}"
            )
    
    def get_books_by_subject(
        self,
        subject: str,
        total_books: int = 1000,
        language: str = "en"
    ) -> List[Dict]:
        """
        Obtiene múltiples libros de una materia específica
        
        Args:
            subject: Materia (ej: "programming", "python", "javascript")
            total_books: Total de libros a obtener
            language: Código de idioma
        
        Returns:
            List[Dict]: Lista de libros con metadatos
        """
        all_books = []
        max_results_per_request = 40
        requests_needed = (total_books + max_results_per_request - 1) // max_results_per_request
        
        print(f"📚 Obteniendo {total_books} libros de '{subject}'...")
        
        for i in range(requests_needed):
            start_index = i * max_results_per_request
            
            try:
                response = self.search_books(
                    query="",
                    subject=subject,
                    max_results=max_results_per_request,
                    start_index=start_index,
                    language=language
                )
                
                items = response.get("items", [])
                if not items:
                    print(f"⚠️ No hay más resultados después de {len(all_books)} libros")
                    break
                
                all_books.extend(items)
                print(f"  ✓ Obtenidos {len(all_books)}/{total_books} libros...")
                
                # Evitar rate limiting
                if i < requests_needed - 1:
                    time.sleep(0.5)
                
                # Si ya tenemos suficientes, detener
                if len(all_books) >= total_books:
                    break
                    
            except Exception as e:
                print(f"⚠️ Error en request {i+1}: {str(e)}")
                # Continuar con los que tenemos
                break
        
        return all_books[:total_books]
    
    def parse_book_metadata(self, book_item: Dict) -> Optional[Dict]:
        """
        Parsea los metadatos de un libro de Google Books
        
        Args:
            book_item: Item de libro de la API
        
        Returns:
            Dict: Metadatos parseados y limpios
        """
        try:
            volume_info = book_item.get("volumeInfo", {})
            
            # Extraer información básica
            titulo = volume_info.get("title")
            if not titulo:
                return None
            
            # Autores
            autores = volume_info.get("authors", [])
            if not autores:
                autores = ["Autor Desconocido"]
            
            # Editorial
            editorial = volume_info.get("publisher", "Editorial Desconocida")
            
            # Páginas
            paginas_totales = volume_info.get("pageCount", 0)
            
            # Sinopsis
            sinopsis = volume_info.get("description", "")
            if sinopsis:
                # Si existe sinopsis, truncar si es muy larga
                if len(sinopsis) > 2000:
                    sinopsis = sinopsis[:1997] + "..."
            else:
                # Si no hay sinopsis, usar valor por defecto
                sinopsis = "Sinopsis no disponible"
            
            # Categorías
            categorias = volume_info.get("categories", [])
            
            # Fecha de publicación
            fecha_publicacion = volume_info.get("publishedDate", "")
            
            # Imagen de portada
            image_links = volume_info.get("imageLinks", {})
            portada_url = image_links.get("thumbnail", "")
            if not portada_url:
                # Si no hay portada, usar imagen por defecto de "no encontrado"
                portada_url = "https://static.vecteezy.com/system/resources/previews/005/377/442/non_2x/404-error-page-icon-page-not-found-line-icon-laptop-with-warning-sign-and-error-404-trouble-internet-connection-concept-file-not-found-and-broken-page-icon-illustration-vector.jpg"
            
            # ISBN
            industry_identifiers = volume_info.get("industryIdentifiers", [])
            isbn = ""
            for identifier in industry_identifiers:
                if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
                    isbn = identifier.get("identifier", "")
                    break
            
            return {
                "titulo": titulo,
                "autores": autores,
                "editorial": editorial,
                "paginas_totales": paginas_totales,
                "sinopsis": sinopsis,
                "categorias": categorias,
                "fecha_publicacion": fecha_publicacion,
                "portada_url": portada_url,
                "isbn": isbn,
                "google_books_id": book_item.get("id", "")
            }
            
        except Exception as e:
            print(f"⚠️ Error al parsear libro: {str(e)}")
            return None
    
    def get_programming_books(
        self,
        total_books: int = 1000,
        subjects: List[str] = None
    ) -> List[Dict]:
        """
        Obtiene libros de programación de múltiples temas
        
        Args:
            total_books: Total de libros a obtener
            subjects: Lista de temas de programación
        
        Returns:
            List[Dict]: Lista de libros parseados
        """
        if subjects is None:
            subjects = [
                # Programación (25 categorías)
                "programming",
                "python programming",
                "javascript programming",
                "java programming",
                "web development",
                "software engineering",
                "computer science",
                "data science",
                "machine learning",
                "algorithms",
                "react programming",
                "angular programming",
                "node.js programming",
                "c++ programming",
                "c# programming",
                "ruby programming",
                "php programming",
                "swift programming",
                "kotlin programming",
                "database design",
                "artificial intelligence",
                "cloud computing",
                "cybersecurity",
                "mobile development",
                "game development",
                
                # Matemáticas y Álgebra (20 categorías)
                "mathematics",
                "algebra",
                "calculus",
                "linear algebra",
                "differential equations",
                "statistics",
                "probability",
                "geometry",
                "trigonometry",
                "discrete mathematics",
                "mathematical analysis",
                "number theory",
                "complex analysis",
                "topology",
                "real analysis",
                "abstract algebra",
                "mathematical logic",
                "combinatorics",
                "numerical analysis",
                "applied mathematics",
                
                # Administración de Empresas (20 categorías)
                "business administration",
                "management",
                "marketing",
                "finance",
                "accounting",
                "human resources",
                "strategic planning",
                "project management",
                "operations management",
                "entrepreneurship",
                "leadership",
                "organizational behavior",
                "business strategy",
                "supply chain management",
                "financial management",
                "business analytics",
                "corporate finance",
                "international business",
                "business ethics",
                "business communication",
                
                # Metodología de Investigación (15 categorías)
                "research methodology",
                "scientific method",
                "qualitative research",
                "quantitative research",
                "research design",
                "data collection",
                "statistical analysis",
                "academic writing",
                "thesis writing",
                "research ethics",
                "experimental design",
                "survey methodology",
                "case study research",
                "action research",
                "literature review",
                
                # Documentación y Gestión de Proyectos (15 categorías)
                "technical writing",
                "documentation",
                "project documentation",
                "software documentation",
                "agile methodology",
                "scrum",
                "project planning",
                "risk management",
                "quality assurance",
                "process improvement",
                "requirements engineering",
                "system documentation",
                "user documentation",
                "api documentation",
                "knowledge management",
                
                # Ciencias Adicionales (10 categorías)
                "physics",
                "chemistry",
                "biology",
                "environmental science",
                "engineering",
                "electrical engineering",
                "mechanical engineering",
                "civil engineering",
                "chemical engineering",
                "materials science"
            ]
        
        # Buscar la cantidad solicitada en CADA categoría hasta alcanzar el objetivo
        all_parsed_books = []
        seen_titles = set()  # Para evitar duplicados
        
        for subject in subjects:
            print(f"\n🔍 Buscando libros de: {subject} (Progreso: {len(all_parsed_books)}/{total_books})")
            
            # Si ya alcanzamos el objetivo, detener
            if len(all_parsed_books) >= total_books:
                print(f"🎯 ¡Objetivo alcanzado! {len(all_parsed_books)} libros únicos obtenidos")
                break
            
            try:
                # Buscar la cantidad total solicitada en esta categoría
                # (se detendrá cuando alcancemos el objetivo global)
                raw_books = self.get_books_by_subject(
                    subject=subject,
                    total_books=total_books,  # Buscar la cantidad completa en cada categoría
                    language="en"
                )
                
                books_added_from_subject = 0
                for raw_book in raw_books:
                    parsed = self.parse_book_metadata(raw_book)
                    if parsed:
                        # Evitar duplicados por título
                        title_lower = parsed["titulo"].lower()
                        if title_lower not in seen_titles:
                            seen_titles.add(title_lower)
                            all_parsed_books.append(parsed)
                            books_added_from_subject += 1
                            
                            # Detener si alcanzamos el límite
                            if len(all_parsed_books) >= total_books:
                                break
                
                print(f"  ✓ Agregados {books_added_from_subject} libros únicos de '{subject}'")
                
            except Exception as e:
                print(f"⚠️ Error al obtener libros de '{subject}': {str(e)}")
                continue
        
        print(f"\n✅ Total de libros únicos obtenidos: {len(all_parsed_books)}")
        return all_parsed_books


# Instancia singleton del servicio
google_books_service = GoogleBooksService()
