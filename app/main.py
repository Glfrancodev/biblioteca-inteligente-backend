from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables
from app.routes import (
    auth_router,
    usuarios_router,
    libros_router,
    editorial_router,
    autor_router,
    admin_router,
    lecturas_router,
    preferencias_router,
    lenguaje_router,
    categoria_router,
    nivel_router,
)
from app.utils.exception_handlers import setup_exception_handlers
from app.utils.responses import create_success_response
import os
from dotenv import load_dotenv

load_dotenv()

# Crear instancia de FastAPI
app = FastAPI(
    title=os.getenv("APP_NAME", "BookApp API"),
    description="API para gestión de biblioteca de libros con usuarios y preferencias",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar manejadores de excepciones personalizados
setup_exception_handlers(app)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Evento de inicio: Crear tablas
@app.on_event("startup")
async def startup_event():
    """Crear las tablas en la base de datos al iniciar la aplicación"""
    try:
        create_tables()
        print("✅ Tablas de base de datos creadas/verificadas")
    except Exception as e:
        print(f"⚠️ Error al crear tablas: {e}")
        print("⚠️ Continuando sin crear tablas...")


# Ruta raíz
@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raíz de la API"""
    return create_success_response(
        data={
            "name": "BookApp API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        message="Bienvenido a BookApp API"
    )


# Endpoint de health check
@app.get("/health", tags=["Health"])
def health_check():
    """Verificar el estado de la API"""
    return create_success_response(
        data={"status": "healthy"},
        message="API está funcionando correctamente"
    )


# Incluir routers
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(libros_router)
app.include_router(editorial_router)
app.include_router(autor_router)
app.include_router(admin_router)
app.include_router(lecturas_router)
app.include_router(preferencias_router)
app.include_router(lenguaje_router)
app.include_router(categoria_router)
app.include_router(nivel_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
