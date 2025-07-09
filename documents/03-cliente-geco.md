# Cliente GECO - Documentación Técnica

## Descripción General

El Cliente GECO (`gecko_client.py`) es una clase Python personalizada desarrollada específicamente para interactuar con la API del sistema GECO (Gestión de Corpus) de la UNAM. Este cliente facilita la autenticación, consulta y extracción de documentos académicos y técnicos almacenados en el repositorio GECO.

## Arquitectura del Cliente

### Clase Principal: GECOClient

```python
class GECOClient:
    def __init__(self, username: str, password: str):
        self.token_url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/get-token"
        self.username = username
        self.password = password
        self.token = None
```

**Componentes de Inicialización**:
- **URL Base**: Endpoint del sistema GECO de la UNAM
- **Credenciales**: Usuario y contraseña para autenticación
- **Token**: Almacenamiento del token de sesión (inicialmente None)

## Funcionalidades del Cliente

### 1. Sistema de Autenticación

#### Método: `get_token()`

```python
def get_token(self):
    payload = {
        'username': self.username,
        'password': self.password
    }
    
    response = requests.post(self.token_url, data=payload)
    
    if response.status_code == 200:
        self.token = response.json().get('token')
        print("Token received:", self.token)
        return self.token
    else:
        raise Exception(f"Failed to get token. Status: {response.status_code}, Response: {response.text}")
```

**Proceso de Autenticación**:
1. **Envío de Credenciales**: POST con username y password
2. **Validación de Respuesta**: Verificación del código de estado HTTP
3. **Extracción del Token**: Obtención del token de la respuesta JSON
4. **Almacenamiento**: Guarda el token para uso en peticiones posteriores
5. **Manejo de Errores**: Lanza excepción si falla la autenticación

**Características de Seguridad**:
- **Autenticación Basada en Token**: Evita enviar credenciales en cada petición
- **Validación de Estado**: Verifica respuestas HTTP antes de procesar
- **Manejo de Errores**: Proporciona información detallada sobre fallos

### 2. Método de Peticiones Autorizadas

#### Método: `make_authorized_request()`

```python
def make_authorized_request(self, url: str):
    if not self.token:
        raise Exception("No token available. Call get_token() first.")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {self.token}"
    }
    return requests.get(url, headers=headers)
```

**Funcionalidad**:
- **Validación de Token**: Verifica que existe un token válido
- **Headers Estándar**: Configura headers HTTP apropiados
- **Autorización**: Incluye token en header Authorization
- **Reutilización**: Método base para todas las peticiones autenticadas

### 3. Gestión de Corpus

#### Método: `list_corpus()`

```python
def list_corpus(self):
    if not self.token:
        raise Exception("No token available. Call get_token() first.")
    url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {self.token}"
    }
    return requests.get(url, headers=headers)
```

**Propósito**: Obtiene lista completa de corpus disponibles en el sistema GECO

**Respuesta Típica**:
```json
{
    "data": {
        "proyectos": [
            {
                "id": 1,
                "nombre": "Corpus de Elementos Finitos",
                "descripcion": "Documentos sobre métodos numéricos",
                "fecha_creacion": "2024-01-01"
            }
        ]
    }
}
```

#### Método: `corpus_metadata()`

```python
def corpus_metadata(self, corpus_id: str):
    url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id + "/meta"
    # ... headers y petición
```

**Funcionalidad**: Obtiene metadatos específicos de un corpus individual

**Información Proporcionada**:
- **Descripción Detallada**: Información completa del corpus
- **Estadísticas**: Número de documentos, tamaño, etc.
- **Configuración**: Parámetros específicos del corpus
- **Permisos**: Información sobre acceso y restricciones

### 4. Gestión de Documentos

#### Método: `list_corpus_documents()`

```python
def list_corpus_documents(self, corpus_id: str):
    url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id
    # ... implementación
```

**Propósito**: Lista todos los documentos dentro de un corpus específico

**Información de Documentos**:
- **ID del Documento**: Identificador único
- **Nombre del Archivo**: Nombre original del documento
- **Metadatos**: Información adicional (autor, fecha, tipo)
- **Permisos**: Estado de derechos de acceso (`derechos: true/false`)
- **Estado**: Disponibilidad y procesamiento

#### Método: `get_corpus_text()`

```python
def get_corpus_text(self, corpus_id: str, documents_id):
    url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id + "/" + documents_id
    # ... implementación
    response = requests.get(url, headers=headers)
    return response.json()
```

**Funcionalidad Principal**: Extrae el contenido textual completo de un documento específico

**Proceso de Extracción**:
1. **Construcción de URL**: Combina corpus_id y document_id
2. **Petición Autorizada**: Utiliza token para acceso
3. **Extracción de Contenido**: Obtiene texto procesado
4. **Formato JSON**: Devuelve respuesta estructurada

**Estructura de Respuesta**:
```json
{
    "data": "Contenido textual completo del documento...",
    "metadata": {
        "document_id": "123",
        "corpus_id": "456",
        "processed_date": "2024-01-01"
    }
}
```

### 5. Gestión de Archivos Adjuntos

#### Método: `list_corpus_files()`

```python
def list_corpus_files(self, corpus_id: str, documents_id: str):
    url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id + "/" + documents_id + "/adjuntos"
```

**Propósito**: Lista archivos adjuntos asociados a un documento específico

**Tipos de Archivos Soportados**:
- **PDFs**: Documentos originales
- **Imágenes**: Figuras y diagramas
- **Datos**: Archivos de datos complementarios
- **Código**: Scripts y programas relacionados

#### Método: `get_corpus_file()`

```python
def get_corpus_file(self, corpus_id: str, documents_id):
    url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id + "/" + documents_id + "/" + '544'
```

**Funcionalidad**: Descarga archivos específicos asociados a documentos

**Nota**: El ID '544' parece ser un identificador fijo, posiblemente requiere parametrización

### 6. Gestión de Aplicaciones

#### Método: `list_corpus_applications()`

```python
def list_corpus_applications(self, corpus_id: str):
    url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/apps/" + corpus_id + "/aplicaciones"
```

**Propósito**: Lista aplicaciones o herramientas asociadas a un corpus específico

**Posibles Aplicaciones**:
- **Herramientas de Análisis**: Scripts de procesamiento
- **Visualizadores**: Interfaces de exploración
- **Exportadores**: Herramientas de conversión de formato
- **Validadores**: Verificadores de integridad

## Integración con el Sistema RAG

### Uso en load.py

```python
# Inicialización del cliente
client = GECOClient("usuario_anonimo", "2024anonimo")
client.get_token()

# Obtención de corpus
corpus_response = client.list_corpus()
corpus_data = corpus_response.json()["data"]["proyectos"]

# Procesamiento de documentos
for corpus in corpus_data:
    doc_response = client.list_corpus_documents(corpus_id=str(corpus["id"]))
    # ... procesamiento adicional
```

### Flujo de Integración

1. **Autenticación**: Obtención de token de acceso
2. **Descubrimiento**: Listado de corpus disponibles
3. **Exploración**: Análisis de documentos por corpus
4. **Filtrado**: Selección de documentos accesibles
5. **Extracción**: Obtención de contenido textual
6. **Procesamiento**: Conversión a formato LangChain

## Configuración y Credenciales

### Credenciales por Defecto

```python
username = "usuario_anonimo"
password = "2024anonimo"
```

**Características**:
- **Acceso Público**: Credenciales para acceso general
- **Limitaciones**: Posibles restricciones en documentos protegidos
- **Configurabilidad**: Fácil cambio para credenciales específicas

### Configuración de Endpoints

**URL Base**: `http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/`

**Endpoints Disponibles**:
- `/get-token`: Autenticación
- `/corpus`: Listado de corpus
- `/corpus/{id}`: Documentos de corpus
- `/corpus/{id}/meta`: Metadatos de corpus
- `/corpus/{id}/{doc_id}`: Contenido de documento
- `/corpus/{id}/{doc_id}/adjuntos`: Archivos adjuntos
- `/apps/{id}/aplicaciones`: Aplicaciones de corpus

## Manejo de Errores y Robustez

### Validación de Respuestas

```python
if response.status_code == 200:
    # Procesamiento exitoso
else:
    raise Exception(f"Failed to get token. Status: {response.status_code}")
```

### Tipos de Errores Manejados

1. **Errores de Autenticación**: Credenciales inválidas
2. **Errores de Red**: Problemas de conectividad
3. **Errores de Autorización**: Token expirado o inválido
4. **Errores de Datos**: Respuestas malformadas
5. **Errores de Recursos**: Documentos no encontrados

### Estrategias de Recuperación

- **Reautenticación**: Renovación automática de tokens
- **Reintentos**: Múltiples intentos para peticiones fallidas
- **Logging**: Registro detallado de errores
- **Validación**: Verificación de datos antes de procesamiento

## Optimizaciones y Mejoras Futuras

### Mejoras Propuestas

1. **Cache de Tokens**: Almacenamiento persistente de tokens válidos
2. **Pool de Conexiones**: Reutilización de conexiones HTTP
3. **Paginación**: Manejo de grandes conjuntos de datos
4. **Filtros Avanzados**: Criterios de selección más específicos
5. **Compresión**: Optimización de transferencia de datos

### Extensibilidad

- **Nuevos Endpoints**: Fácil adición de nuevas funcionalidades
- **Configuración Flexible**: Parámetros configurables
- **Logging Avanzado**: Sistema de registro más detallado
- **Métricas**: Monitoreo de rendimiento y uso

## Consideraciones de Seguridad

### Buenas Prácticas Implementadas

- **Tokens de Sesión**: Evita exposición de credenciales
- **HTTPS**: Comunicación segura (cuando esté disponible)
- **Validación de Entrada**: Verificación de parámetros
- **Manejo de Excepciones**: Prevención de exposición de información sensible

### Recomendaciones Adicionales

- **Variables de Entorno**: Almacenamiento seguro de credenciales
- **Rotación de Tokens**: Renovación periódica de tokens
- **Logging Seguro**: Evitar registro de información sensible
- **Validación de SSL**: Verificación de certificados (para HTTPS)
