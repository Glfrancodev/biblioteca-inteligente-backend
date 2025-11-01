"""
Script de migración para agregar columna urlPortada a la tabla libros
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener credenciales de .env
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bookapp")

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    
    # Verificar si la columna ya existe
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='libros' AND column_name='urlPortada'
    """)
    
    if cursor.fetchone():
        print("✅ La columna 'urlPortada' ya existe en la tabla 'libros'")
    else:
        # Agregar la columna
        cursor.execute("""
            ALTER TABLE libros ADD COLUMN "urlPortada" VARCHAR(500);
        """)
        conn.commit()
        print("✅ Columna 'urlPortada' agregada exitosamente a la tabla 'libros'")
    
    cursor.close()
    conn.close()
    print("✅ Migración completada")
    
except Exception as e:
    print(f"❌ Error en la migración: {str(e)}")
    print("\nIntenta ejecutar manualmente:")
    print('ALTER TABLE libros ADD COLUMN "urlPortada" VARCHAR(500);')
