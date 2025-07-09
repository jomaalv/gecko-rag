# Sistema de Ingesta de Datos - load.py

## Descripción General

El archivo `load.py` es el componente central del sistema de ingesta de datos de Gecko RAG. Su función principal es inicializar y poblar la base de datos vectorial Qdrant con todos los documentos del corpus GECO3, procesándolos y convirtiéndolos en embeddings vectoriales para búsqueda semántica.

## Funcionalidad Principal

### Propósito
- **Inicialización del Sistema**: Prepara la base de datos vectorial con documentos procesados
- **Ingesta Masiva**: Procesa todos los corpus disponibles en GECO de forma automatizada
- **Transformación de Datos**: Convierte texto plano en representaciones vectoriales

### Integración en la Arquitectura

![Diagrama de Arquitectura](./diagram.png)

El proceso de ingesta (`load.py`) es fundamental para poblar el sistema mostrado en el diagrama:
- **Conecta con la API GECO** externa para obtener documentos
- **Utiliza all-MiniLM-L6-v2** para generar embeddings de 384 dimensiones
- **Almacena en Qdrant** (puerto 6333) la colección `corpus_gecko3`
- **Prepara los datos** que luego utilizarán ambos servicios backend (puertos 8000 y 8002)

## Proceso de Ingesta Detallado

### 1. Configuración Inicial

```python
# Configuración del modelo de embeddings
embedding_model = HuggingFaceEmbeddings(
    model_name="./local_models/all-MiniLM-L6-v2"
)

# Conexión a Qdrant
qdrant = QdrantClient(
    host="qdrant",
    port=6333,
    https=False
)

# Configuración de la colección
collection_name = "corpus_gecko3"
```

**Características de la Configuración**:
- **Modelo Local**: Utiliza modelo de embeddings almacenado localmente
- **Colección Específica**: Crea colección dedicada para corpus GECO3
- **Parámetros Vectoriales**: 384 dimensiones con distancia coseno

### 2. Preparación de la Base de Datos

```python
# Eliminación y recreación de colección
if qdrant.collection_exists(collection_name=collection_name):
    qdrant.delete_collection(collection_name=collection_name)
    print("colección eliminada: ", collection_name)

qdrant.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
```

**Proceso de Preparación**:
- **Limpieza**: Elimina colección existente para evitar duplicados
- **Recreación**: Crea nueva colección con parámetros optimizados
- **Configuración Vectorial**: 384 dimensiones (compatible con all-MiniLM-L6-v2)

### 3. Autenticación y Conexión GECO

```python
client = GECOClient("usuario_anonimo", "2024anonimo")
client.get_token()

corpus_response = client.list_corpus()
corpus_data = corpus_response.json()["data"]["proyectos"]
```

**Proceso de Autenticación**:
- **Cliente GECO**: Instancia del cliente personalizado
- **Obtención de Token**: Autenticación automática
- **Listado de Corpus**: Recupera todos los corpus disponibles

### 4. Procesamiento de Documentos

#### 4.1 Iteración por Corpus

```python
corpus_count = str(len(corpus_data))
for j, corpus in enumerate(corpus_data):
    corpus_id = str(corpus["id"])
    corpus_name = str(corpus["nombre"])
```

#### 4.2 Extracción de Documentos

```python
doc_response = client.list_corpus_documents(corpus_id=corpus_id)
if doc_response.status_code == 200:
    doc_data = doc_response.json().get("data", [])
```

#### 4.3 Filtrado por Permisos

```python
if document['derechos'] is False:
    response = client.get_corpus_text(
        corpus_id=str(corpus_id), 
        documents_id=str(document['id'])
    )
```

**Criterios de Filtrado**:
- **Derechos de Acceso**: Solo procesa documentos sin restricciones
- **Disponibilidad**: Verifica que el contenido esté accesible
- **Integridad**: Valida que el documento tenga contenido

### 5. Normalización de Metadatos

```python
document['archivo'] = re.sub(r'[()\s]', lambda m: '_' if m.group(0) == ' ' else '', 
    unicodedata.normalize('NFKD', document['archivo'])
    .encode('ascii', 'ignore')
    .decode('utf-8')
)
```

**Proceso de Normalización**:
- **Eliminación de Acentos**: Convierte caracteres especiales a ASCII
- **Reemplazo de Espacios**: Sustituye espacios por guiones bajos
- **Limpieza de Caracteres**: Elimina paréntesis y caracteres problemáticos

### 6. Creación de Documentos LangChain

```python
docs.append(Document(
    page_content=response["data"], 
    metadata={
        "source": str(document['archivo']), 
        "corpus_id": str(corpus_id), 
        "corpus_name": corpus_name, 
        "document": str(document['id']), 
        "chunk": '1'
    }
))
```

**Estructura de Metadatos**:
- **source**: Nombre del archivo normalizado
- **corpus_id**: Identificador único del corpus
- **corpus_name**: Nombre descriptivo del corpus
- **document**: ID del documento original
- **chunk**: Número de fragmento (para documentos segmentados)

### 7. Segmentación de Texto

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500, 
    chunk_overlap=200
)
split_docs = splitter.split_documents(docs)
```

**Parámetros de Segmentación**:
- **Tamaño de Fragmento**: 1500 caracteres por chunk
- **Solapamiento**: 200 caracteres entre fragmentos consecutivos
- **Método**: Segmentación recursiva que respeta estructura del texto

### 8. Generación de Embeddings y Almacenamiento

```python
vector_store = Qdrant.from_documents(
    documents=split_docs,
    embedding=embedding_model,
    location="http://" + host + ":6333",
    collection_name=collection_name,
)
```

**Proceso de Vectorización**:
- **Generación de Embeddings**: Convierte texto a vectores de 384 dimensiones
- **Almacenamiento**: Guarda vectores y metadatos en Qdrant
- **Indexación**: Crea índices para búsqueda eficiente

## Estadísticas y Monitoreo

### Información de Procesamiento

```python
text_length = len(response["data"])
print("Corpus id: ", str(corpus_id))
print("Text Document Size: ", text_length)
print("Number of Docs: ", str(len(docs)))
```

**Métricas Monitoreadas**:
- **ID del Corpus**: Identificación del corpus procesado
- **Tamaño del Texto**: Longitud total del contenido
- **Número de Documentos**: Cantidad de documentos procesados
- **Fragmentos Generados**: Número de chunks creados

## Optimizaciones y Consideraciones

### Eficiencia de Procesamiento
- **Procesamiento Batch**: Procesa múltiples documentos por corpus
- **Validación de Contenido**: Evita procesar documentos vacíos
- **Manejo de Errores**: Continúa procesamiento aunque falle un documento

### Gestión de Memoria
- **Limpieza de Variables**: Reutiliza estructuras de datos
- **Procesamiento Incremental**: Procesa un corpus a la vez
- **Liberación de Recursos**: Gestión eficiente de memoria

### Robustez del Sistema
- **Manejo de Excepciones**: Captura y registra errores
- **Validación de Respuestas**: Verifica códigos de estado HTTP
- **Recuperación de Errores**: Continúa procesamiento tras fallos

## Configuración del Modelo de Embeddings

### Modelo all-MiniLM-L6-v2

**Características del Modelo**:
- **Arquitectura**: Transformer basado en BERT
- **Dimensiones**: 384 vectores
- **Idiomas**: Multilingüe (optimizado para inglés, funcional en español)
- **Rendimiento**: Balance entre calidad y velocidad
- **Tamaño**: ~90MB (modelo compacto)

**Ventajas para el Proyecto**:
- **Eficiencia**: Rápida generación de embeddings
- **Calidad**: Buena representación semántica
- **Compatibilidad**: Funciona bien con contenido técnico
- **Recursos**: Requisitos computacionales moderados

### Almacenamiento Local

```python
model_name="./local_models/all-MiniLM-L6-v2"
```

**Beneficios del Almacenamiento Local**:
- **Independencia**: No requiere conexión a internet durante ejecución
- **Velocidad**: Carga más rápida del modelo
- **Consistencia**: Versión fija del modelo
- **Privacidad**: No envía datos a servicios externos

## Resultados del Proceso

### Estructura Final en Qdrant

Cada documento procesado genera:
- **Vector de 384 dimensiones**: Representación semántica del contenido
- **Metadatos completos**: Información de origen y estructura
- **Índices de búsqueda**: Optimizados para consultas rápidas
- **Relaciones preservadas**: Mantiene vínculos entre documentos

### Capacidades de Búsqueda

Una vez completada la ingesta:
- **Búsqueda Semántica**: Encuentra documentos por significado, no solo palabras clave
- **Filtrado por Metadatos**: Búsqueda específica por corpus o tipo de documento
- **Ranking por Relevancia**: Ordena resultados por similitud semántica
- **Recuperación Contextual**: Mantiene contexto de fragmentos relacionados

## Mantenimiento y Actualizaciones

### Reingesta de Datos
- **Proceso Completo**: Elimina y recrea toda la colección
- **Actualización Incremental**: Posible modificación para actualizaciones parciales
- **Verificación de Integridad**: Validación post-ingesta

### Monitoreo de Calidad
- **Métricas de Procesamiento**: Documentos procesados vs. disponibles
- **Calidad de Embeddings**: Verificación de representaciones vectoriales
- **Integridad de Metadatos**: Validación de información asociada
