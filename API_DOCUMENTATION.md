# 📚 Documentación de API - BookApp Backend

**Versión:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Fecha:** 31 de Octubre, 2025

---

## 📋 Tabla de Contenidos

1. [Información General](#información-general)
2. [Autenticación](#autenticación)
3. [Endpoints](#endpoints)
   - [Root & Health](#root--health)
   - [Autenticación](#endpoints-de-autenticación)
   - [Usuarios](#endpoints-de-usuarios)
   - [Libros](#endpoints-de-libros)
   - [Editoriales](#endpoints-de-editoriales)
   - [Autores](#endpoints-de-autores)
   - [Lecturas](#endpoints-de-lecturas)
   - [Preferencias](#endpoints-de-preferencias)
   - [Lenguajes](#endpoints-de-lenguajes)
   - [Categorías](#endpoints-de-categorías)
4. [Modelos de Datos](#modelos-de-datos)
5. [Códigos de Error](#códigos-de-error)

---

## 🌐 Información General

### Formato de Respuesta Estándar

Todas las respuestas de la API siguen un formato consistente:

#### Respuesta Exitosa

```json
{
  "success": true,
  "data": {
    /* datos de respuesta */
  },
  "message": "Operación exitosa",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Nota:** Cuando la respuesta contiene una lista de elementos, se incluye el campo `count`:

```json
{
  "success": true,
  "data": [
    /* array de elementos */
  ],
  "message": "Elementos obtenidos exitosamente",
  "count": 25,
  "timestamp": "2025-10-31T12:00:00"
}
```

#### Respuesta de Error

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Descripción del error",
    "details": null
  },
  "timestamp": "2025-10-31T12:00:00"
}
```

### Autenticación

La API utiliza **JWT (JSON Web Tokens)** para autenticación. Después de iniciar sesión, incluye el token en el header de autorización:

```
Authorization: Bearer <tu_token_aqui>
```

---

## 📍 Endpoints

### Root & Health

#### `GET /`

Endpoint raíz de la API - Información básica

**Autenticación:** No requerida

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "name": "BookApp API",
    "version": "1.0.0",
    "docs": "/docs",
    "redoc": "/redoc"
  },
  "message": "Bienvenido a BookApp API",
  "timestamp": "2025-10-31T12:00:00"
}
```

#### `GET /health`

Verificar estado de la API

**Autenticación:** No requerida

**Respuesta:**

```json
{
  "success": true,
  "data": {
    "status": "healthy"
  },
  "message": "API está funcionando correctamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

### Endpoints de Autenticación

#### `POST /auth/register`

Registrar un nuevo usuario

**Autenticación:** No requerida

**Body:**

```json
{
  "registro": "2021001",
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "1234567890",
  "password": "password123"
}
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "data": {
    "idUsuario": 1,
    "registro": "2021001",
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "1234567890",
    "estado": "activo",
    "creado_en": "2025-10-31T12:00:00",
    "actualizado_en": "2025-10-31T12:00:00"
  },
  "message": "Usuario registrado exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `400 - USER_003`: Email ya está registrado
- `400 - USER_004`: Registro ya está en uso

---

#### `POST /auth/login`

Iniciar sesión

**Autenticación:** No requerida

**Body:**

```json
{
  "email": "juan@example.com",
  "password": "password123"
}
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Inicio de sesión exitoso",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `401 - AUTH_001`: Email o contraseña incorrectos

---

### Endpoints de Usuarios

#### `GET /usuarios/me`

Obtener información del usuario actual

**Autenticación:** Requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idUsuario": 1,
    "registro": "2021001",
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "1234567890",
    "estado": "activo",
    "creado_en": "2025-10-31T12:00:00",
    "actualizado_en": "2025-10-31T12:00:00"
  },
  "message": "Usuario obtenido exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `401 - AUTH_004`: No autorizado

---

#### `GET /usuarios`

Obtener lista de usuarios

**Autenticación:** Requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idUsuario": 1,
      "registro": "2021001",
      "nombre": "Juan Pérez",
      "email": "juan@example.com",
      "telefono": "1234567890",
      "estado": "activo",
      "creado_en": "2025-10-31T12:00:00",
      "actualizado_en": "2025-10-31T12:00:00"
    }
  ],
  "message": "1 usuarios obtenidos exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /usuarios/{usuario_id}`

Obtener un usuario específico

**Autenticación:** Requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idUsuario": 1,
    "registro": "2021001",
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "1234567890",
    "estado": "activo",
    "creado_en": "2025-10-31T12:00:00",
    "actualizado_en": "2025-10-31T12:00:00"
  },
  "message": "Usuario obtenido exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - USER_001`: Usuario no encontrado

---

#### `PUT /usuarios/{usuario_id}`

Actualizar información de usuario

**Autenticación:** Requerida (solo puede actualizar su propia información)

**Body:**

```json
{
  "nombre": "Juan Carlos Pérez",
  "telefono": "0987654321"
}
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idUsuario": 1,
    "registro": "2021001",
    "nombre": "Juan Carlos Pérez",
    "email": "juan@example.com",
    "telefono": "0987654321",
    "estado": "activo",
    "creado_en": "2025-10-31T12:00:00",
    "actualizado_en": "2025-10-31T12:30:00"
  },
  "message": "Usuario actualizado exitosamente",
  "timestamp": "2025-10-31T12:30:00"
}
```

**Posibles Errores:**

- `403 - AUTH_005`: No tienes permiso para actualizar este usuario
- `404 - USER_001`: Usuario no encontrado

---

#### `DELETE /usuarios/{usuario_id}`

Eliminar usuario

**Autenticación:** Requerida (solo puede eliminar su propia cuenta)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "deleted": true,
    "id": 1
  },
  "message": "Usuario eliminado exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `403 - AUTH_005`: No tienes permiso para eliminar este usuario
- `404 - USER_001`: Usuario no encontrado

---

### Endpoints de Libros

#### `POST /libros`

Crear un nuevo libro

**Autenticación:** Requerida

**Body:**

```json
{
  "titulo": "Cien Años de Soledad",
  "totalPaginas": 417,
  "sinopsis": "Una novela del escritor colombiano...",
  "urlLibro": "https://ejemplo.com/libro.pdf",
  "idEditorial": 1,
  "autores_ids": [1, 2]
}
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "data": {
    "idLibro": 1,
    "titulo": "Cien Años de Soledad",
    "totalPaginas": 417,
    "sinopsis": "Una novela del escritor colombiano...",
    "urlLibro": "https://ejemplo.com/libro.pdf",
    "idEditorial": 1,
    "editorial": {
      "idEditorial": 1,
      "nombre": "Editorial Sudamericana"
    },
    "autores": [
      {
        "idAutor": 1,
        "nombre": "Gabriel García Márquez"
      }
    ]
  },
  "message": "Libro creado exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - BOOK_002`: Editorial no encontrada
- `404 - BOOK_003`: Uno o más autores no encontrados

---

#### `GET /libros`

Obtener lista de libros

**Autenticación:** No requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idLibro": 1,
      "titulo": "Cien Años de Soledad",
      "totalPaginas": 417,
      "sinopsis": "Una novela del escritor colombiano...",
      "urlLibro": "https://ejemplo.com/libro.pdf",
      "idEditorial": 1,
      "editorial": {
        "idEditorial": 1,
        "nombre": "Editorial Sudamericana"
      },
      "autores": [
        {
          "idAutor": 1,
          "nombre": "Gabriel García Márquez"
        }
      ]
    }
  ],
  "message": "1 libros obtenidos exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /libros/{libro_id}`

Obtener un libro específico

**Autenticación:** No requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idLibro": 1,
    "titulo": "Cien Años de Soledad",
    "totalPaginas": 417,
    "sinopsis": "Una novela del escritor colombiano...",
    "urlLibro": "https://ejemplo.com/libro.pdf",
    "idEditorial": 1,
    "editorial": {
      "idEditorial": 1,
      "nombre": "Editorial Sudamericana"
    },
    "autores": [
      {
        "idAutor": 1,
        "nombre": "Gabriel García Márquez"
      }
    ]
  },
  "message": "Libro obtenido exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - BOOK_001`: Libro no encontrado

---

#### `PUT /libros/{libro_id}`

Actualizar un libro

**Autenticación:** Requerida

**Body:**

```json
{
  "titulo": "Cien Años de Soledad (Edición especial)",
  "totalPaginas": 450,
  "autores_ids": [1]
}
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idLibro": 1,
    "titulo": "Cien Años de Soledad (Edición especial)",
    "totalPaginas": 450,
    "sinopsis": "Una novela del escritor colombiano...",
    "urlLibro": "https://ejemplo.com/libro.pdf",
    "idEditorial": 1,
    "editorial": {
      "idEditorial": 1,
      "nombre": "Editorial Sudamericana"
    },
    "autores": [
      {
        "idAutor": 1,
        "nombre": "Gabriel García Márquez"
      }
    ]
  },
  "message": "Libro actualizado exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - BOOK_001`: Libro no encontrado

---

#### `DELETE /libros/{libro_id}`

Eliminar un libro

**Autenticación:** Requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "deleted": true,
    "id": 1
  },
  "message": "Libro eliminado exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - BOOK_001`: Libro no encontrado

---

### Endpoints de Editoriales

#### `POST /editoriales`

Crear una nueva editorial

**Autenticación:** Requerida

**Body:**

```json
{
  "nombre": "Editorial Planeta"
}
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "data": {
    "idEditorial": 1,
    "nombre": "Editorial Planeta"
  },
  "message": "Editorial creada exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /editoriales`

Obtener lista de editoriales

**Autenticación:** No requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idEditorial": 1,
      "nombre": "Editorial Planeta"
    },
    {
      "idEditorial": 2,
      "nombre": "Editorial Sudamericana"
    }
  ],
  "message": "2 editoriales obtenidas exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

### Endpoints de Autores

#### `POST /autores`

Crear un nuevo autor

**Autenticación:** Requerida

**Body:**

```json
{
  "nombre": "Gabriel García Márquez"
}
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "data": {
    "idAutor": 1,
    "nombre": "Gabriel García Márquez"
  },
  "message": "Autor creado exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /autores`

Obtener lista de autores

**Autenticación:** No requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idAutor": 1,
      "nombre": "Gabriel García Márquez"
    },
    {
      "idAutor": 2,
      "nombre": "Isabel Allende"
    }
  ],
  "message": "2 autores obtenidos exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

### Endpoints de Lecturas

#### `POST /lecturas`

Crear una nueva lectura para el usuario actual

**Autenticación:** Requerida

**Body:**

```json
{
  "idLibro": 1,
  "paginaLeidas": 50,
  "estado": "en_progreso"
}
```

**Valores válidos para `estado`:**

- `no_iniciado`
- `en_progreso`
- `completado`
- `abandonado`

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "data": {
    "idLectura": 1,
    "idUsuario": 1,
    "idLibro": 1,
    "paginaLeidas": 50,
    "estado": "en_progreso"
  },
  "message": "Lectura creada exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - BOOK_001`: Libro no encontrado
- `400 - READING_002`: Ya tienes una lectura registrada para este libro

---

#### `GET /lecturas`

Obtener todas las lecturas del usuario actual

**Autenticación:** Requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idLectura": 1,
      "idUsuario": 1,
      "idLibro": 1,
      "paginaLeidas": 50,
      "estado": "en_progreso",
      "libro_titulo": "Cien Años de Soledad",
      "libro_total_paginas": 417,
      "progreso_porcentaje": 11.99
    }
  ],
  "message": "Lecturas obtenidas exitosamente",
  "count": 1,
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /lecturas/{lectura_id}`

Obtener una lectura específica

**Autenticación:** Requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idLectura": 1,
    "idUsuario": 1,
    "idLibro": 1,
    "paginaLeidas": 50,
    "estado": "en_progreso",
    "libro_titulo": "Cien Años de Soledad",
    "libro_total_paginas": 417,
    "progreso_porcentaje": 11.99
  },
  "message": "Lectura obtenida exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - READING_001`: Lectura no encontrada

---

#### `PUT /lecturas/{lectura_id}`

Actualizar el progreso de una lectura

**Autenticación:** Requerida

**Body:**

```json
{
  "paginaLeidas": 200,
  "estado": "en_progreso"
}
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idLectura": 1,
    "idUsuario": 1,
    "idLibro": 1,
    "paginaLeidas": 200,
    "estado": "en_progreso"
  },
  "message": "Lectura actualizada exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - READING_001`: Lectura no encontrada
- `400 - READING_003`: Las páginas leídas no pueden exceder el total

---

#### `DELETE /lecturas/{lectura_id}`

Eliminar una lectura

**Autenticación:** Requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "deleted": true,
    "id": 1
  },
  "message": "Lectura eliminada exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - READING_001`: Lectura no encontrada

---

#### `GET /lecturas/estado/completados`

Obtener todos los libros completados del usuario actual

**Autenticación:** Requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idLectura": 5,
      "idUsuario": 1,
      "idLibro": 3,
      "paginaLeidas": 417,
      "estado": "completado",
      "libro_titulo": "Cien Años de Soledad",
      "libro_total_paginas": 417,
      "progreso_porcentaje": 100.0,
      "url_firmada": "https://semilleros-frontend.s3.amazonaws.com/libros/...",
      "urlPortada": "https://books.google.com/books/content?id=..."
    },
    {
      "idLectura": 8,
      "idUsuario": 1,
      "idLibro": 7,
      "paginaLeidas": 328,
      "estado": "completado",
      "libro_titulo": "1984",
      "libro_total_paginas": 328,
      "progreso_porcentaje": 100.0,
      "url_firmada": null,
      "urlPortada": "https://books.google.com/books/content?id=..."
    }
  ],
  "message": "Libros completados obtenidos exitosamente",
  "count": 2,
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /lecturas/estado/en-progreso`

Obtener todos los libros en progreso del usuario actual

**Autenticación:** Requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idLectura": 12,
      "idUsuario": 1,
      "idLibro": 5,
      "paginaLeidas": 150,
      "estado": "en_progreso",
      "libro_titulo": "Clean Code",
      "libro_total_paginas": 464,
      "progreso_porcentaje": 32.33,
      "url_firmada": "https://semilleros-frontend.s3.amazonaws.com/libros/...",
      "urlPortada": "https://books.google.com/books/content?id=..."
    },
    {
      "idLectura": 15,
      "idUsuario": 1,
      "idLibro": 9,
      "paginaLeidas": 87,
      "estado": "en_progreso",
      "libro_titulo": "El Principito",
      "libro_total_paginas": 96,
      "progreso_porcentaje": 90.63,
      "url_firmada": null,
      "urlPortada": "https://books.google.com/books/content?id=..."
    }
  ],
  "message": "Libros en progreso obtenidos exitosamente",
  "count": 2,
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /lecturas/estadisticas/paginas-leidas`

Obtener el total de páginas leídas por el usuario actual

**Autenticación:** Requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "total_paginas_leidas": 5847,
    "total_lecturas": 25,
    "promedio_paginas_por_lectura": 233.88,
    "usuario_id": 1,
    "usuario_nombre": "Juan Pérez"
  },
  "message": "Total de páginas leídas: 5847",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

### Endpoints de Preferencias

#### `POST /preferencias`

Crear preferencias para el usuario actual

**Autenticación:** Requerida

**Body:**

```json
{
  "lenguajes_ids": [1, 2],
  "categorias_ids": [3, 4, 5]
}
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "data": {
    "idPreferencias": 1,
    "idUsuario": 1,
    "creada_en": "2025-10-31T12:00:00",
    "lenguajes": [
      {
        "idLenguaje": 1,
        "nombre": "Español"
      },
      {
        "idLenguaje": 2,
        "nombre": "Inglés"
      }
    ],
    "categorias": [
      {
        "idCategoria": 3,
        "nombre": "Ficción"
      },
      {
        "idCategoria": 4,
        "nombre": "Ciencia"
      },
      {
        "idCategoria": 5,
        "nombre": "Historia"
      }
    ]
  },
  "message": "Preferencias creadas exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `400 - PREF_002`: El usuario ya tiene preferencias configuradas. Use PUT para actualizar.

---

#### `GET /preferencias/me`

Obtener las preferencias del usuario actual

**Autenticación:** Requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idPreferencias": 1,
    "idUsuario": 1,
    "creada_en": "2025-10-31T12:00:00",
    "lenguajes": [
      {
        "idLenguaje": 1,
        "nombre": "Español"
      },
      {
        "idLenguaje": 2,
        "nombre": "Inglés"
      }
    ],
    "categorias": [
      {
        "idCategoria": 3,
        "nombre": "Ficción"
      },
      {
        "idCategoria": 4,
        "nombre": "Ciencia"
      }
    ]
  },
  "message": "Preferencias obtenidas exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - PREF_001`: El usuario no tiene preferencias configuradas

---

#### `PUT /preferencias/me`

Actualizar las preferencias del usuario actual

**Autenticación:** Requerida

**Body:**

```json
{
  "lenguajes_ids": [1, 3],
  "categorias_ids": [5, 6]
}
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "idPreferencias": 1,
    "idUsuario": 1,
    "creada_en": "2025-10-31T12:00:00",
    "lenguajes": [
      {
        "idLenguaje": 1,
        "nombre": "Español"
      },
      {
        "idLenguaje": 3,
        "nombre": "Francés"
      }
    ],
    "categorias": [
      {
        "idCategoria": 5,
        "nombre": "Historia"
      },
      {
        "idCategoria": 6,
        "nombre": "Biografía"
      }
    ]
  },
  "message": "Preferencias actualizadas exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - PREF_001`: El usuario no tiene preferencias configuradas. Use POST para crear.

---

#### `DELETE /preferencias/me`

Eliminar las preferencias del usuario actual

**Autenticación:** Requerida

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "deleted": true
  },
  "message": "Preferencias eliminadas exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

**Posibles Errores:**

- `404 - PREF_001`: El usuario no tiene preferencias configuradas

---

### Endpoints de Lenguajes

#### `POST /lenguajes`

Crear un nuevo lenguaje

**Autenticación:** Requerida

**Body:**

```json
{
  "nombre": "Español"
}
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "data": {
    "idLenguaje": 1,
    "nombre": "Español"
  },
  "message": "Lenguaje creado exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /lenguajes`

Obtener lista de lenguajes disponibles

**Autenticación:** No requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idLenguaje": 1,
      "nombre": "Español"
    },
    {
      "idLenguaje": 2,
      "nombre": "Inglés"
    },
    {
      "idLenguaje": 3,
      "nombre": "Francés"
    }
  ],
  "message": "3 lenguajes obtenidos exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

### Endpoints de Categorías

#### `POST /categorias`

Crear una nueva categoría

**Autenticación:** Requerida

**Body:**

```json
{
  "nombre": "Ficción"
}
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "data": {
    "idCategoria": 1,
    "nombre": "Ficción"
  },
  "message": "Categoría creada exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

#### `GET /categorias`

Obtener lista de categorías disponibles

**Autenticación:** No requerida

**Query Parameters:**

- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros (default: 100)

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "idCategoria": 1,
      "nombre": "Ficción"
    },
    {
      "idCategoria": 2,
      "nombre": "No Ficción"
    },
    {
      "idCategoria": 3,
      "nombre": "Ciencia"
    }
  ],
  "message": "3 categorías obtenidas exitosamente",
  "timestamp": "2025-10-31T12:00:00"
}
```

---

## 📊 Modelos de Datos

### Usuario

```typescript
{
  idUsuario: number;
  registro: string;
  nombre: string;
  email: string;
  telefono?: string;
  estado: "activo" | "inactivo" | "suspendido";
  creado_en: string; // ISO 8601
  actualizado_en: string; // ISO 8601
}
```

### Libro

```typescript
{
  idLibro: number;
  titulo: string;
  totalPaginas: number;
  sinopsis?: string;
  urlLibro?: string;
  idEditorial: number;
  editorial: {
    idEditorial: number;
    nombre: string;
  };
  autores: Array<{
    idAutor: number;
    nombre: string;
  }>;
}
```

### Lectura

```typescript
{
  idLectura: number;
  idUsuario: number;
  idLibro: number;
  paginaLeidas: number;
  estado: "no_iniciado" | "en_progreso" | "completado" | "abandonado";
  libro_titulo?: string;
  libro_total_paginas?: number;
  progreso_porcentaje?: number;
}
```

### Preferencia

```typescript
{
  idPreferencias: number;
  idUsuario: number;
  creada_en: string; // ISO 8601
  lenguajes: Array<{
    idLenguaje: number;
    nombre: string;
  }>;
  categorias: Array<{
    idCategoria: number;
    nombre: string;
  }>;
}
```

---

## ⚠️ Códigos de Error

### Autenticación (AUTH)

| Código   | Descripción            |
| -------- | ---------------------- |
| AUTH_001 | Credenciales inválidas |
| AUTH_002 | Token expirado         |
| AUTH_003 | Token inválido         |
| AUTH_004 | No autorizado          |
| AUTH_005 | Permisos insuficientes |

### Usuarios (USER)

| Código   | Descripción           |
| -------- | --------------------- |
| USER_001 | Usuario no encontrado |
| USER_002 | Usuario ya existe     |
| USER_003 | Email ya registrado   |
| USER_004 | Registro ya en uso    |
| USER_005 | Usuario inactivo      |

### Libros (BOOK)

| Código   | Descripción             |
| -------- | ----------------------- |
| BOOK_001 | Libro no encontrado     |
| BOOK_002 | Editorial no encontrada |
| BOOK_003 | Autor no encontrado     |

### Lecturas (READING)

| Código      | Descripción           |
| ----------- | --------------------- |
| READING_001 | Lectura no encontrada |
| READING_002 | Lectura ya existe     |
| READING_003 | Páginas exceden total |

### Preferencias (PREF)

| Código   | Descripción               |
| -------- | ------------------------- |
| PREF_001 | Preferencia no encontrada |
| PREF_002 | Preferencia ya existe     |
| PREF_003 | Lenguaje no encontrado    |
| PREF_004 | Categoría no encontrada   |

### Validación (VAL)

| Código  | Descripción         |
| ------- | ------------------- |
| VAL_001 | Error de validación |
| VAL_002 | Entrada inválida    |

### Sistema (SYS)

| Código  | Descripción                |
| ------- | -------------------------- |
| SYS_001 | Error interno del servidor |
| SYS_002 | Error de base de datos     |
| SYS_003 | Recurso no encontrado      |

---

## 📝 Notas Adicionales

### Paginación

La mayoría de endpoints que devuelven listas soportan paginación mediante los parámetros:

- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros a devolver (default: 100)

### Validaciones Comunes

- **Email**: Debe ser un email válido
- **Contraseña**: Mínimo 6 caracteres
- **Nombre**: Mínimo 2 caracteres
- **Registro**: Mínimo 3 caracteres
- **Páginas leídas**: No puede ser negativo ni exceder el total de páginas del libro

### Estados de Usuario

- `activo`: Usuario activo en el sistema
- `inactivo`: Usuario inactivo
- `suspendido`: Usuario suspendido temporalmente

### Estados de Lectura

- `no_iniciado`: El libro no ha sido iniciado
- `en_progreso`: Lectura en curso
- `completado`: Lectura finalizada
- `abandonado`: Lectura abandonada

### Documentación Interactiva

Puedes acceder a la documentación interactiva de Swagger en:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔗 Enlaces Útiles

- **Repositorio**: Glfrancodev/biblioteca-inteligente-backend
- **Branch**: main
- **Versión API**: 1.0.0
- **Fecha de documento**: 31 de Octubre, 2025

---

_Generado automáticamente para el proyecto BookApp Backend_
