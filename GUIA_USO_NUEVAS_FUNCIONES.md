# Guía de Uso - Nuevas Funcionalidades

## 🚀 Instalación de Dependencias

Primero, instala las nuevas dependencias:

```cmd
pip install -r requirements.txt
```

## 📋 Configuración

Las credenciales de AWS S3 ya están configuradas en tu archivo `.env`:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION
- AWS_BUCKET_NAME

## 🎯 Funcionalidad 1: Subir Libros con PDF

### Endpoint: `POST /libros/with-file`

**Tipo**: `multipart/form-data`

**Headers**:

```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Body (Form Data)**:

- `titulo`: string
- `totalPaginas`: integer
- `sinopsis`: string
- `idEditorial`: integer
- `autores_ids`: string (JSON array, ej: "[1,2,3]")
- `file`: PDF file

**Ejemplo con curl**:

```cmd
curl -X POST "http://localhost:8000/libros/with-file" ^
  -H "Authorization: Bearer tu_token_aqui" ^
  -F "titulo=Clean Code" ^
  -F "totalPaginas=464" ^
  -F "sinopsis=A handbook of agile software craftsmanship" ^
  -F "idEditorial=1" ^
  -F "autores_ids=[1]" ^
  -F "file=@ruta/al/archivo.pdf"
```

**Respuesta Exitosa**:

```json
{
  "success": true,
  "data": {
    "idLibro": 1,
    "titulo": "Clean Code",
    "totalPaginas": 464,
    "sinopsis": "...",
    "urlLibro": "libros/clean_code_20251031_123456_abc123.pdf",
    "url_firmada": "https://semilleros-frontend.s3.us-east-2.amazonaws.com/...",
    "idEditorial": 1,
    "autores": [...]
  },
  "message": "Libro creado exitosamente con archivo PDF"
}
```

**Notas Importantes**:

- ✅ El PDF se sube automáticamente a S3
- ✅ Se guarda la **key de S3** en `urlLibro` (no la URL firmada)
- ✅ La **URL firmada** se devuelve en la respuesta (válida por 7 días)
- ✅ Solo se permiten archivos PDF

---

## 📚 Funcionalidad 2: Poblar Base de Datos desde Google Books

### Endpoint: `POST /admin/populate-books`

**Tipo**: `application/json`

**Headers**:

```
Authorization: Bearer {token}
Content-Type: application/json
```

**Query Parameters**:

- `total_books`: integer (opcional, default: 1000, máx: 5000)

**Ejemplo con curl**:

```cmd
curl -X POST "http://localhost:8000/admin/populate-books?total_books=500" ^
  -H "Authorization: Bearer tu_token_aqui" ^
  -H "Content-Type: application/json"
```

**Respuesta**:

```json
{
  "success": true,
  "data": {
    "status": "En proceso",
    "total_solicitado": 500,
    "mensaje": "La población de libros se está ejecutando en segundo plano"
  },
  "message": "Proceso de población iniciado"
}
```

**Categorías que se Consultan**:

- Programming
- Python Programming
- JavaScript Programming
- Java Programming
- Web Development
- Software Engineering
- Computer Science
- Data Science
- Machine Learning
- Algorithms

**Qué se Guarda**:

- ✅ Título, sinopsis, páginas totales
- ✅ Autores (creados automáticamente si no existen)
- ✅ Editoriales (creadas automáticamente si no existen)
- ✅ `urlLibro = NULL` (sin PDF, solo metadatos)
- ✅ Se evitan duplicados (mismo título + editorial)

---

### Endpoint: `GET /admin/populate-status`

Ver estadísticas de la base de datos:

```cmd
curl -X GET "http://localhost:8000/admin/populate-status"
```

**Respuesta**:

```json
{
  "success": true,
  "data": {
    "total_libros": 1243,
    "total_autores": 567,
    "total_editoriales": 89,
    "libros_con_pdf": 23,
    "libros_sin_pdf": 1220
  },
  "message": "Estadísticas obtenidas exitosamente"
}
```

---

## 🔐 URLs Firmadas de S3

### Endpoint: `GET /libros/{libro_id}`

Cuando consultas un libro que tiene PDF en S3, la respuesta incluye automáticamente una **URL firmada**:

```json
{
  "success": true,
  "data": {
    "idLibro": 1,
    "titulo": "Clean Code",
    "urlLibro": "libros/clean_code_20251031_123456_abc123.pdf",
    "url_firmada": "https://semilleros-frontend.s3.us-east-2.amazonaws.com/...",
    ...
  }
}
```

**Notas**:

- ✅ La URL firmada es válida por **7 días**
- ✅ Permite acceso directo desde el navegador
- ✅ No requiere autenticación adicional
- ✅ Si `urlLibro` es `null`, `url_firmada` también será `null`

---

## 🎨 Estructura de Datos

### Libro con PDF Real:

```json
{
  "idLibro": 1,
  "titulo": "Clean Code",
  "totalPaginas": 464,
  "urlLibro": "libros/clean_code_20251031_123456.pdf", // Key de S3
  "url_firmada": "https://..." // URL temporal
}
```

### Libro sin PDF (Solo Metadatos):

```json
{
  "idLibro": 2,
  "titulo": "Python Crash Course",
  "totalPaginas": 544,
  "urlLibro": null, // Sin PDF
  "url_firmada": null // Sin URL
}
```

---

## 🛠️ Flujo de Trabajo Recomendado

### 1. Poblar la Base de Datos

```cmd
# Obtener 2000 libros de Google Books
POST /admin/populate-books?total_books=2000
```

### 2. Ver Estadísticas

```cmd
GET /admin/populate-status
```

### 3. Subir PDFs Reales (Opcional)

```cmd
# Para libros que consigas PDFs reales
POST /libros/with-file
```

### 4. Consultar Libros en el Frontend

```javascript
// GET /libros/{id}
if (libro.url_firmada) {
  // Mostrar PDF real
  <PDFViewer url={libro.url_firmada} />;
} else {
  // Mostrar simulación
  <PDFSimulado totalPages={libro.totalPaginas} />;
}
```

---

## ⚠️ Limitaciones y Consideraciones

### Google Books API:

- ⚠️ Límite: ~1000 requests/día (API gratuita)
- ⚠️ Para 5000 libros puede tomar ~10-20 minutos
- ⚠️ Algunos libros pueden no tener todos los metadatos

### AWS S3:

- ✅ URLs firmadas válidas por 7 días
- ✅ Debes regenerar URL si ha expirado (automático al consultar)
- ✅ Storage: ~$0.023/GB/mes

---

## 🧪 Testing

### 1. Test de Upload:

```cmd
# Crear editorial y autor primero
POST /editoriales
POST /autores

# Luego subir libro con PDF
POST /libros/with-file
```

### 2. Test de Población:

```cmd
# Poblar con pocos libros para probar
POST /admin/populate-books?total_books=50
```

### 3. Verificar URLs:

```cmd
# Obtener libro y verificar url_firmada
GET /libros/1
```

---

## 📊 Monitoreo

Ver logs en la terminal donde corre uvicorn:

- ✅ `✅ Archivo subido exitosamente: libros/...`
- 📚 `📚 Obteniendo X libros de 'programming'...`
- ✅ `✅ Total de libros obtenidos: X`
- ⚠️ `⚠️ Error al...` (si hay problemas)

---

## 🎯 Próximos Pasos

1. **Frontend**: Implementar componente de simulación de PDF
2. **Búsqueda**: Agregar filtros por categoría, autor, etc.
3. **Recomendaciones**: Usar metadatos para ML
4. **Migración**: Gradualmente agregar PDFs reales a libros importantes

¡Todo listo para usar! 🚀
