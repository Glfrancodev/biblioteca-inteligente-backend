"""
Servicio de recomendaciones basado en K-Means
Sistema simple para usuarios nuevos usando solo:
- Preferencias de categorías
- Preferencias de lenguajes
- Nivel del usuario
"""
from typing import List, Dict
from sqlalchemy.orm import Session, selectinload
from app.models.usuario import Usuario
from app.models.libro import Libro, LibroCategoria, LibroLenguaje, AutorLibro
from app.models.preferencia import Categoria, Lenguaje
from app.models.nivel import Nivel
from app.models import EstadoUsuario
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os


class RecommendationService:
    """Servicio de recomendaciones con K-Means"""
    
    def __init__(self):
        self.model_path = "models/kmeans_model.pkl"
        self.scaler_path = "models/scaler.pkl"
        self.clusters_path = "models/user_clusters.npy"
    
    def extract_user_features(self, usuario: Usuario, db: Session) -> np.ndarray:
        """
        Extrae features del usuario para K-Means
        
        Vector de características:
        - One-hot encoding de categorías (todas las categorías existentes)
        - One-hot encoding de lenguajes (todos los lenguajes existentes)
        - Nivel normalizado (1=Principiante, 2=Intermedio, 3=Avanzado)
        """
        # Obtener todas las categorías y lenguajes disponibles (para dimensión fija)
        all_categorias = db.query(Categoria).order_by(Categoria.idCategoria).all()
        all_lenguajes = db.query(Lenguaje).order_by(Lenguaje.idLenguaje).all()
        
        # Obtener preferencias del usuario
        preferencia = usuario.preferencia
        
        if not preferencia:
            # Si no tiene preferencias, retornar vector de ceros
            return np.zeros(len(all_categorias) + len(all_lenguajes) + 1)
        
        # One-hot encoding de categorías del usuario
        user_categoria_ids = {pc.idCategoria for pc in preferencia.preferencia_categorias}
        categorias_vector = [1 if cat.idCategoria in user_categoria_ids else 0 
                            for cat in all_categorias]
        
        # One-hot encoding de lenguajes del usuario
        user_lenguaje_ids = {pl.idLenguaje for pl in preferencia.preferencia_lenguajes}
        lenguajes_vector = [1 if lang.idLenguaje in user_lenguaje_ids else 0 
                           for lang in all_lenguajes]
        
        # Nivel normalizado (1, 2, 3 -> 0.33, 0.66, 1.0)
        nivel_value = preferencia.idNivel / 3.0 if preferencia.idNivel else 0.33
        
        # Combinar todos los features
        feature_vector = categorias_vector + lenguajes_vector + [nivel_value]
        
        return np.array(feature_vector)
    
    def train_model(self, db: Session, n_clusters: int = 5):
        """
        Entrena el modelo K-Means con todos los usuarios
        
        Args:
            db: Sesión de base de datos
            n_clusters: Número de clusters (default: 5)
        """
        print("Entrenando modelo de recomendaciones...")
        
        # Obtener todos los usuarios activos
        usuarios = db.query(Usuario).filter(Usuario.estado == EstadoUsuario.ACTIVO).all()
        
        if len(usuarios) < n_clusters:
            print(f"Advertencia: Solo hay {len(usuarios)} usuarios, ajustando clusters a {len(usuarios)}")
            n_clusters = max(2, len(usuarios))
        
        # Extraer features de todos los usuarios
        user_ids = []
        feature_vectors = []
        
        for usuario in usuarios:
            user_ids.append(usuario.idUsuario)
            features = self.extract_user_features(usuario, db)
            feature_vectors.append(features)
        
        X = np.array(feature_vectors)
        
        # Normalizar features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entrenar K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Crear directorio de modelos si no existe
        os.makedirs("models", exist_ok=True)
        
        # Guardar modelo y scaler
        joblib.dump(kmeans, self.model_path)
        joblib.dump(scaler, self.scaler_path)
        
        # Guardar clusters de usuarios
        user_cluster_map = {user_id: int(cluster) 
                           for user_id, cluster in zip(user_ids, clusters)}
        np.save(self.clusters_path, user_cluster_map)
        
        print(f"✓ Modelo entrenado con {len(usuarios)} usuarios en {n_clusters} clusters")
        print(f"✓ Modelo guardado en: {self.model_path}")
        
        return user_cluster_map
    
    def get_user_cluster(self, usuario: Usuario, db: Session) -> int:
        """
        Obtiene el cluster del usuario usando el modelo entrenado
        
        Args:
            usuario: Usuario a clasificar
            db: Sesión de base de datos
            
        Returns:
            int: ID del cluster
        """
        # Cargar modelo y scaler
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            print("Modelo no encontrado, entrenando...")
            self.train_model(db)
        
        kmeans = joblib.load(self.model_path)
        scaler = joblib.load(self.scaler_path)
        
        # Extraer features del usuario
        user_features = self.extract_user_features(usuario, db)
        user_features_scaled = scaler.transform([user_features])
        
        # Predecir cluster
        cluster = kmeans.predict(user_features_scaled)[0]
        
        return int(cluster)
    
    def get_recommendations(self, usuario_id: int, db: Session, limit: int = 10) -> List[Dict]:
        """
        Obtiene recomendaciones para un usuario basadas en su cluster
        
        Args:
            usuario_id: ID del usuario
            db: Sesión de base de datos
            limit: Número de recomendaciones (default: 10)
            
        Returns:
            Lista de libros recomendados con detalles
        """
        # Obtener usuario
        usuario = db.query(Usuario).filter(Usuario.idUsuario == usuario_id).first()
        if not usuario:
            return []
        
        # Obtener cluster del usuario
        try:
            user_cluster = self.get_user_cluster(usuario, db)
        except Exception as e:
            print(f"Error al obtener cluster: {e}")
            # Fallback: recomendar libros por categorías/lenguajes preferidos
            return self._fallback_recommendations(usuario, db, limit)
        
        # Cargar mapa de clusters
        if os.path.exists(self.clusters_path):
            user_cluster_map = np.load(self.clusters_path, allow_pickle=True).item()
        else:
            user_cluster_map = {}
        
        # Encontrar usuarios del mismo cluster
        usuarios_similares_ids = [uid for uid, cluster in user_cluster_map.items() 
                                 if cluster == user_cluster and uid != usuario_id]
        
        # Si no hay usuarios similares, usar fallback
        if not usuarios_similares_ids:
            return self._fallback_recommendations(usuario, db, limit)
        
        # Obtener libros de usuarios similares
        # Por ahora, recomendar libros que tengan las mismas categorías/lenguajes
        preferencia = usuario.preferencia
        
        if not preferencia:
            return self._fallback_recommendations(usuario, db, limit)
        
        user_categoria_ids = {pc.idCategoria for pc in preferencia.preferencia_categorias}
        user_lenguaje_ids = {pl.idLenguaje for pl in preferencia.preferencia_lenguajes}
        
        # Query de libros que coincidan con preferencias
        query = db.query(Libro)
        
        # Filtrar por categorías o lenguajes
        if user_categoria_ids or user_lenguaje_ids:
            # Obtener libros que tengan al menos una categoría o lenguaje en común
            libro_ids = set()
            
            if user_categoria_ids:
                categoria_libros = db.query(LibroCategoria.idLibro).filter(
                    LibroCategoria.idCategoria.in_(list(user_categoria_ids))
                ).all()
                libro_ids.update([lb.idLibro for lb in categoria_libros])
            
            if user_lenguaje_ids:
                lenguaje_libros = db.query(LibroLenguaje.idLibro).filter(
                    LibroLenguaje.idLenguaje.in_(list(user_lenguaje_ids))
                ).all()
                libro_ids.update([lb.idLibro for lb in lenguaje_libros])
            
            if libro_ids:
                query = query.filter(Libro.idLibro.in_(list(libro_ids)))
        
        # Obtener libros con eager loading
        libros = (
            query.options(
                selectinload(Libro.editorial),
                selectinload(Libro.autor_libros).selectinload(AutorLibro.autor),
                selectinload(Libro.libro_categorias).selectinload(LibroCategoria.categoria),
                selectinload(Libro.libro_lenguajes).selectinload(LibroLenguaje.lenguaje)
            )
            .order_by(Libro.idLibro.desc())
            .limit(limit)
            .all()
        )
        
        # Si no hay suficientes, usar fallback
        if len(libros) < limit:
            # Obtener IDs de libros ya recomendados
            libros_ids_existentes = {libro.idLibro for libro in libros}
            fallback = self._fallback_recommendations(usuario, db, limit - len(libros), libros_ids_existentes)
            libros.extend(fallback)
        
        # Eliminar duplicados manteniendo el orden
        libros_unicos = []
        libros_ids_vistos = set()
        for libro in libros:
            if libro.idLibro not in libros_ids_vistos:
                libros_unicos.append(libro)
                libros_ids_vistos.add(libro.idLibro)
        
        # Formatear respuesta
        recomendaciones = []
        for libro in libros_unicos[:limit]:
            recomendaciones.append({
                "idLibro": libro.idLibro,
                "titulo": libro.titulo,
                "sinopsis": libro.sinopsis,
                "urlPortada": libro.urlPortada,
                "urlLibro": libro.urlLibro,
                "totalPaginas": libro.totalPaginas,
                "autores": [{"idAutor": al.autor.idAutor, "nombre": al.autor.nombre} 
                           for al in libro.autor_libros],
                "categorias": [{"idCategoria": lc.categoria.idCategoria, "nombre": lc.categoria.nombre}
                              for lc in libro.libro_categorias],
                "lenguajes": [{"idLenguaje": ll.lenguaje.idLenguaje, "nombre": ll.lenguaje.nombre}
                             for ll in libro.libro_lenguajes],
            })
        
        return recomendaciones
    
    def _fallback_recommendations(self, usuario: Usuario, db: Session, limit: int, excluir_ids: set = None) -> List[Libro]:
        """
        Recomendaciones de respaldo cuando no hay cluster o usuarios similares
        Retorna libros que coincidan con categorías/lenguajes preferidos
        
        Args:
            usuario: Usuario para quien se buscan recomendaciones
            db: Sesión de base de datos
            limit: Número máximo de libros a retornar
            excluir_ids: Set de IDs de libros a excluir
        """
        if excluir_ids is None:
            excluir_ids = set()
        
        preferencia = usuario.preferencia
        
        if not preferencia:
            # Sin preferencias, retornar libros más recientes (excluyendo los ya recomendados)
            query = db.query(Libro)
            if excluir_ids:
                query = query.filter(~Libro.idLibro.in_(list(excluir_ids)))
            return query.order_by(Libro.idLibro.desc()).limit(limit).all()
        
        user_categoria_ids = {pc.idCategoria for pc in preferencia.preferencia_categorias}
        user_lenguaje_ids = {pl.idLenguaje for pl in preferencia.preferencia_lenguajes}
        
        # Si tiene preferencias, buscar por ellas
        if user_categoria_ids or user_lenguaje_ids:
            libro_ids = set()
            
            if user_categoria_ids:
                categoria_libros = db.query(LibroCategoria.idLibro).filter(
                    LibroCategoria.idCategoria.in_(list(user_categoria_ids))
                ).all()
                libro_ids.update([lb.idLibro for lb in categoria_libros])
            
            if user_lenguaje_ids:
                lenguaje_libros = db.query(LibroLenguaje.idLibro).filter(
                    LibroLenguaje.idLenguaje.in_(list(user_lenguaje_ids))
                ).all()
                libro_ids.update([lb.idLibro for lb in lenguaje_libros])
            
            # Excluir libros ya recomendados
            if excluir_ids:
                libro_ids -= excluir_ids
            
            if libro_ids:
                libros = db.query(Libro).filter(
                    Libro.idLibro.in_(list(libro_ids))
                ).order_by(Libro.idLibro.desc()).limit(limit).all()
            else:
                # Si no quedan libros, buscar cualquier libro no excluido
                query = db.query(Libro)
                if excluir_ids:
                    query = query.filter(~Libro.idLibro.in_(list(excluir_ids)))
                libros = query.order_by(Libro.idLibro.desc()).limit(limit).all()
        else:
            # Sin preferencias, retornar libros más recientes (excluyendo los ya recomendados)
            query = db.query(Libro)
            if excluir_ids:
                query = query.filter(~Libro.idLibro.in_(list(excluir_ids)))
            libros = query.order_by(Libro.idLibro.desc()).limit(limit).all()
        
        return libros


# Instancia singleton del servicio
recommendation_service = RecommendationService()
