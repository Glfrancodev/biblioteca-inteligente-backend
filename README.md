# BookApp API - FastAPI Backend

Sistema de gestión de biblioteca de libros con usuarios y preferencias.

## Estructura del Proyecto

```
IngenieriaEnCalidad/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── models/              # Modelos SQLAlchemy (Base de datos)
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── libro.py
│   │   ├── lectura.py
│   │   └── preferencia.py
│   ├── schemas/             # Esquemas Pydantic (Validación)
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── libro.py
│   │   ├── lectura.py
│   │   └── preferencia.py
│   ├── routes/              # Endpoints API
│   │   ├── __init__.py
│   │   ├── usuarios.py
│   │   ├── libros.py
│   │   ├── lecturas.py
│   │   └── preferencias.py
│   ├── services/            # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── recommendations.py
│   ├── database/            # Configuración de base de datos
│   │   ├── __init__.py
│   │   └── session.py
│   └── utils/               # Utilidades
│       ├── __init__.py
│       └── security.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requisitos Previos

- Python 3.9 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd IngenieriaEnCalidad
```

### 2. Crear y activar entorno virtual

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

Crear la base de datos en PostgreSQL:

```sql
CREATE DATABASE bookapp;
```

### 5. Configurar variables de entorno

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Editar el archivo `.env` con tus configuraciones:

```env
# Database
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bookapp

# Security
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=BookApp API
```

### 6. Poblar la base de datos con datos iniciales

Antes de ejecutar la aplicación, poblar la base de datos con niveles, lenguajes y categorías iniciales:

```bash
python -m app.seed_data
```

Esto creará:

- 3 niveles: Principiante, Intermedio, Avanzado
- 12 lenguajes de programación: Python, JavaScript, Java, C++, C#, TypeScript, Go, Rust, PHP, Ruby, Swift, Kotlin
- 10 categorías: Algoritmos, Desarrollo Web, Desarrollo Móvil, IA, ML, BD, Seguridad, DevOps, Cloud, Arquitectura

### 7. Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: **http://127.0.0.1:8000**

## Documentación API

Una vez ejecutada la aplicación, acceder a:

- **Swagger UI**: http://127.0.0.1:8000/docs (Interfaz interactiva)
- **ReDoc**: http://127.0.0.1:8000/redoc (Documentación detallada)
- **Documentación completa**: Ver archivo `API_ENDPOINTS.md`

## Autenticación

La API utiliza JWT (JSON Web Tokens) para autenticación:

1. **Registrar usuario**: `POST /auth/register`
2. **Iniciar sesión**: `POST /auth/login` - Retorna un `access_token`
3. **Usar token**: En Swagger, click en "Authorize" y pega el token
4. Los endpoints protegidos automáticamente usarán el token

## Modelos Principales

- **Usuario**: Gestión de usuarios y autenticación JWT
- **Libro**: Catálogo de libros con autores y editoriales
- **Lectura**: Seguimiento del progreso de lectura por usuario
- **Preferencia**: Gestión de preferencias de lenguaje y categorías

## Tecnologías

- **FastAPI 0.115.0**: Framework web moderno y rápido
- **SQLAlchemy 2.0.35**: ORM para base de datos
- **PostgreSQL**: Base de datos relacional
- **Pydantic 2.9.2**: Validación de datos
- **JWT**: Autenticación con tokens
- **Bcrypt**: Hash seguro de contraseñas
- **Uvicorn**: Servidor ASGI

## Características

✅ Autenticación JWT con tokens seguros  
✅ Sistema de roles (activo/inactivo)  
✅ CRUD completo para todas las entidades  
✅ Validación automática con Pydantic  
✅ Respuestas estandarizadas con códigos de error  
✅ Documentación interactiva con Swagger  
✅ Manejo global de excepciones  
✅ CORS configurado  
✅ Variables de entorno seguras

## Endpoints Disponibles

- **Autenticación** (2): Register, Login
- **Usuarios** (6): CRUD + perfil
- **Libros** (5): CRUD + listado
- **Editoriales** (5): CRUD completo
- **Autores** (5): CRUD completo
- **Lecturas** (5): CRUD + progreso
- **Preferencias** (5): CRUD + lenguajes/categorías
- **Lenguajes** (2): Crear, listar
- **Categorías** (2): Crear, listar

**Total: 31 endpoints**

## Desarrollo

Para ver los cambios en tiempo real, el servidor se recarga automáticamente con `--reload`.

Para ver las consultas SQL en consola, `echo=True` está activado en `database/session.py`.

## Producción

Antes de desplegar en producción:

1. Cambiar `SECRET_KEY` en `.env`
2. Configurar `allow_origins` específicos en CORS (main.py)
3. Desactivar `echo=True` en database/session.py
4. Configurar variables de entorno en el servidor
5. Usar un servidor de producción (no `--reload`)
