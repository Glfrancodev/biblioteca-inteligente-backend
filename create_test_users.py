"""
Script para crear usuarios de prueba con preferencias aleatorias pero realistas
Para entrenar el modelo de recomendaciones K-Means
"""
import sys
from pathlib import Path
import random

sys.path.append(str(Path(__file__).parent.parent))

from app.database.session import SessionLocal
from app.models.usuario import Usuario
from app.models.preferencia import Categoria, Lenguaje, Preferencia, PreferenciaCategoria, PreferenciaLenguaje
from app.models.nivel import Nivel
from app.models import EstadoUsuario
from app.utils.security import get_password_hash


# Perfiles de usuarios realistas
PERFILES = [
    {
        "nombre": "Ana García",
        "email": "ana.garcia@example.com",
        "perfil": "Frontend Developer",
        "categorias": ["Desarrollo Web", "Arquitectura de Software"],
        "lenguajes": ["JavaScript", "TypeScript", "Python"],
        "nivel": "Intermedio"
    },
    {
        "nombre": "Carlos Rodríguez",
        "email": "carlos.rodriguez@example.com",
        "perfil": "Backend Developer",
        "categorias": ["Desarrollo Web", "Bases de Datos", "Cloud Computing"],
        "lenguajes": ["Java", "PHP", "Go"],
        "nivel": "Avanzado"
    },
    {
        "nombre": "María López",
        "email": "maria.lopez@example.com",
        "perfil": "Data Scientist",
        "categorias": ["Machine Learning", "Inteligencia Artificial", "Algoritmos y Estructuras de Datos"],
        "lenguajes": ["Python", "C++"],
        "nivel": "Avanzado"
    },
    {
        "nombre": "Juan Pérez",
        "email": "juan.perez@example.com",
        "perfil": "Mobile Developer",
        "categorias": ["Desarrollo Móvil", "Desarrollo Web"],
        "lenguajes": ["Swift", "Kotlin", "JavaScript"],
        "nivel": "Intermedio"
    },
    {
        "nombre": "Laura Martínez",
        "email": "laura.martinez@example.com",
        "perfil": "Security Analyst",
        "categorias": ["Seguridad Informática", "Algoritmos y Estructuras de Datos"],
        "lenguajes": ["C++", "Rust", "Python"],
        "nivel": "Avanzado"
    },
    {
        "nombre": "Pedro Sánchez",
        "email": "pedro.sanchez@example.com",
        "perfil": "DevOps Engineer",
        "categorias": ["DevOps", "Cloud Computing", "Bases de Datos"],
        "lenguajes": ["Go", "Python", "Ruby"],
        "nivel": "Intermedio"
    },
    {
        "nombre": "Sofía Torres",
        "email": "sofia.torres@example.com",
        "perfil": "Full Stack Developer",
        "categorias": ["Desarrollo Web", "Bases de Datos", "DevOps"],
        "lenguajes": ["JavaScript", "Ruby", "PHP", "Python"],
        "nivel": "Avanzado"
    },
    {
        "nombre": "Diego Ramírez",
        "email": "diego.ramirez@example.com",
        "perfil": "Beginner Programmer",
        "categorias": ["Desarrollo Web"],
        "lenguajes": ["JavaScript", "Python"],
        "nivel": "Principiante"
    },
    {
        "nombre": "Valentina Cruz",
        "email": "valentina.cruz@example.com",
        "perfil": "Systems Architect",
        "categorias": ["Arquitectura de Software", "Cloud Computing", "Bases de Datos"],
        "lenguajes": ["Java", "C#", "Python"],
        "nivel": "Avanzado"
    },
    {
        "nombre": "Andrés Morales",
        "email": "andres.morales@example.com",
        "perfil": "Algorithm Expert",
        "categorias": ["Algoritmos y Estructuras de Datos", "Machine Learning"],
        "lenguajes": ["C++", "Rust", "Python"],
        "nivel": "Avanzado"
    },
    {
        "nombre": "Camila Flores",
        "email": "camila.flores@example.com",
        "perfil": "Web Developer Junior",
        "categorias": ["Desarrollo Web"],
        "lenguajes": ["TypeScript", "JavaScript"],
        "nivel": "Principiante"
    },
    {
        "nombre": "Roberto Vargas",
        "email": "roberto.vargas@example.com",
        "perfil": "Database Admin",
        "categorias": ["Bases de Datos", "DevOps"],
        "lenguajes": ["PHP", "Python", "Java"],
        "nivel": "Intermedio"
    },
    {
        "nombre": "Isabella Herrera",
        "email": "isabella.herrera@example.com",
        "perfil": "ML Engineer",
        "categorias": ["Machine Learning", "Inteligencia Artificial", "Cloud Computing"],
        "lenguajes": ["Rust", "Python", "Go"],
        "nivel": "Intermedio"
    },
    {
        "nombre": "Sebastián Díaz",
        "email": "sebastian.diaz@example.com",
        "perfil": "Game Developer",
        "categorias": ["Desarrollo Móvil", "Algoritmos y Estructuras de Datos"],
        "lenguajes": ["C++", "C#", "Rust"],
        "nivel": "Intermedio"
    },
    {
        "nombre": "Gabriela Ruiz",
        "email": "gabriela.ruiz@example.com",
        "perfil": "Cloud Specialist",
        "categorias": ["Cloud Computing", "DevOps", "Seguridad Informática"],
        "lenguajes": ["Go", "Kotlin", "Python"],
        "nivel": "Avanzado"
    }
]


def crear_usuarios_prueba():
    """Crea usuarios de prueba con preferencias realistas"""
    db = SessionLocal()
    
    try:
        # Obtener todas las categorías, lenguajes y niveles
        categorias_db = {cat.nombre: cat for cat in db.query(Categoria).all()}
        lenguajes_db = {lang.nombre: lang for lang in db.query(Lenguaje).all()}
        niveles_db = {nivel.nombre: nivel for nivel in db.query(Nivel).all()}
        
        print(f"Categorías disponibles: {len(categorias_db)}")
        print(f"Lenguajes disponibles: {len(lenguajes_db)}")
        print(f"Niveles disponibles: {len(niveles_db)}\n")
        
        usuarios_creados = 0
        
        for perfil in PERFILES:
            # Verificar si el usuario ya existe
            exists = db.query(Usuario).filter(Usuario.email == perfil["email"]).first()
            if exists:
                print(f"⚠️  Usuario ya existe: {perfil['email']}")
                continue
            
            # Crear usuario
            usuario = Usuario(
                nombre=perfil["nombre"],
                email=perfil["email"],
                registro="user_" + perfil["email"].split("@")[0],
                password=get_password_hash("password123"),  # Contraseña simple para pruebas
                estado=EstadoUsuario.ACTIVO
            )
            
            db.add(usuario)
            db.flush()  # Para obtener el ID del usuario
            
            # Crear registro de preferencia
            preferencia = Preferencia(
                idUsuario=usuario.idUsuario
            )
            
            # Asignar nivel
            nivel_nombre = perfil["nivel"]
            if nivel_nombre in niveles_db:
                preferencia.idNivel = niveles_db[nivel_nombre].idNivel
            
            db.add(preferencia)
            db.flush()  # Para obtener el ID de preferencia
            
            # Agregar preferencias de categorías
            categorias_agregadas = []
            for cat_nombre in perfil["categorias"]:
                if cat_nombre in categorias_db:
                    pref_cat = PreferenciaCategoria(
                        idPreferencias=preferencia.idPreferencias,
                        idCategoria=categorias_db[cat_nombre].idCategoria
                    )
                    db.add(pref_cat)
                    categorias_agregadas.append(cat_nombre)
            
            # Agregar preferencias de lenguajes
            lenguajes_agregados = []
            for lang_nombre in perfil["lenguajes"]:
                if lang_nombre in lenguajes_db:
                    pref_lang = PreferenciaLenguaje(
                        idPreferencias=preferencia.idPreferencias,
                        idLenguaje=lenguajes_db[lang_nombre].idLenguaje
                    )
                    db.add(pref_lang)
                    lenguajes_agregados.append(lang_nombre)
            
            db.commit()
            
            print(f"✓ Usuario creado: {usuario.nombre}")
            print(f"  Email: {usuario.email}")
            print(f"  Perfil: {perfil['perfil']}")
            print(f"  Nivel: {nivel_nombre}")
            print(f"  Categorías: {', '.join(categorias_agregadas)}")
            print(f"  Lenguajes: {', '.join(lenguajes_agregados)}")
            print()
            
            usuarios_creados += 1
        
        print(f"{'='*60}")
        print(f"✓ Total usuarios creados: {usuarios_creados}")
        print(f"{'='*60}")
        print(f"\nCredenciales para todos los usuarios:")
        print(f"  Contraseña: password123")
        print(f"\nAhora puedes entrenar el modelo con:")
        print(f"  GET /recomendaciones/entrenar?n_clusters=5")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    crear_usuarios_prueba()
