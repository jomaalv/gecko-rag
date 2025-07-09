# Servicios Backend - Documentación Técnica

## Descripción General

El sistema Gecko RAG implementa dos servicios backend complementarios, cada uno optimizado para diferentes casos de uso y patrones de consulta. Ambos servicios están construidos con FastAPI y utilizan LangChain para el procesamiento de lenguaje natural.

## Arquitectura de Servicios Backend

![Diagrama de Arquitectura](./diagram.png)

Como se muestra en el diagrama, ambos servicios backend:
- **Utilizan el modelo all-MiniLM-L6-v2** para embeddings (384 dimensiones)
- **Se comunican con Qdrant** (puerto 6333) para búsqueda vectorial
- **Interactúan con Ollama** (puerto 11435) para generación con Llama3
- **Exponen APIs REST** en puertos diferentes (8000 y 8002)

## Servicio Backend Principal (langchain-app)

### Ubicación y Puerto
- **Directorio**: `/langchain-app/`
- **Puerto**: 8000
- **Contenedor**: `langchain-backend`

### Arquitectura Avanzada

#### Pipeline RAG con LangGraph

El servicio principal implementa un pipeline sofisticado utilizando LangGraph para orquestar el flujo de procesamiento:

```python
class State(TypedDict):
    question: str
    query: Search
    context: List[Document]
    answer: str
```

**Estados del Pipeline**:
1. **question**: Pregunta original del usuario
2. **query**: Consulta estructurada y analizada
3. **context**: Documentos recuperados relevantes
4. **answer**: Respuesta generada final

#### Análisis Estructurado de Consultas

```python
class Search(TypedDict):
    query: Annotated[str, ..., "Search query to run."]
    section: Annotated[
        Literal["aprendiendo_sobre_el_metodo_de_los_elementos_finitos.txt", 
                "mtds.txt", "ame1co.txt", "ame1cr.txt", "ame1jn.txt"],
        ..., "Section to query."
    ]
```

**Funcionalidad del Análisis**:
- **Clasificación Automática**: Determina la sección más relevante para la consulta
- **Optimización de Consulta**: Reformula la pregunta para mejor recuperación
- **Filtrado Inteligente**: Dirige la búsqueda a documentos específicos

#### Secciones de Documentos Soportadas

1. **aprendiendo_sobre_el_metodo_de_los_elementos_finitos.txt**
   - Contenido educativo sobre elementos finitos
   - Conceptos fundamentales y aplicaciones

2. **mtds.txt**
   - Métodos numéricos y técnicas computacionales
   - Algoritmos y implementaciones

3. **ame1co.txt**
   - Análisis matemático especializado
   - Contenido técnico avanzado

4. **ame1cr.txt**
   - Criterios y metodologías de análisis
   - Estándares y procedimientos

5. **ame1jn.txt**
   - Contenido específico de dominio
   - Aplicaciones particulares

### Flujo de Procesamiento

#### 1. Función `analyze_query()`

```python
def analyze_query(state: State):
    structured_llm = llm.with_structured_output(Search)
    query = structured_llm.invoke(state["question"])
    return {"query": query}
```

**Proceso**:
- **LLM Estructurado**: Utiliza Llama3 para análisis semántico
- **Clasificación**: Determina sección objetivo y reformula consulta
- **Salida Estructurada**: Genera objeto Search con query y section

#### 2. Función `retrieve()`

```python
def retrieve(state: State):
    query = state["query"]
    retrieved_docs = vector_store.similarity_search(
        query["query"], k=5,
        filter={"source": query["section"]}
    )
    return {"context": retrieved_docs}
```

**Características**:
- **Búsqueda Filtrada**: Limita búsqueda a sección específica
- **Top-K Retrieval**: Recupera los 5 documentos más relevantes
- **Filtrado por Metadatos**: Utiliza campo "source" para filtrar

#### 3. Función `generate()`

```python
def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}
```

**Proceso de Generación**:
- **Concatenación de Contexto**: Une documentos recuperados
- **Prompt Engineering**: Utiliza template de RAG optimizado
- **Generación**: Produce respuesta contextualizada

### Configuración del Grafo

```python
graph_builder = StateGraph(State).add_sequence([analyze_query, retrieve, generate])
graph_builder.add_edge(START, "analyze_query")
graph = graph_builder.compile()
```

**Ventajas del Grafo**:
- **Flujo Secuencial**: Procesamiento ordenado y predecible
- **Estado Compartido**: Información persistente entre etapas
- **Extensibilidad**: Fácil adición de nuevas etapas

### API Endpoint

```python
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    steps = graph.invoke({"question": request.question})
    return {"answer": steps["answer"]}
```

**Características**:
- **Entrada**: JSON con campo "question"
- **Procesamiento**: Ejecuta pipeline completo
- **Salida**: JSON con respuesta generada

## Servicio Backend QA (langchain-app-qa)

### Ubicación y Puerto
- **Directorio**: `/langchain-app-qa/`
- **Puerto**: 8002
- **Contenedor**: `langchain-backend-qa`

### Arquitectura Simplificada

#### RetrievalQA Chain

```python
retriever = vectorstore.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 5}
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"
)
```

**Características**:
- **Búsqueda Global**: Sin filtrado por secciones
- **Chain Type "Stuff"**: Concatena todos los documentos recuperados
- **Simplicidad**: Procesamiento directo sin análisis previo

### Ventajas del Servicio QA

1. **Velocidad**: Procesamiento más rápido sin análisis de consulta
2. **Simplicidad**: Menos complejidad en el pipeline
3. **Cobertura Amplia**: Busca en todo el corpus sin restricciones
4. **Compatibilidad**: API similar al servicio principal

### API Endpoint

```python
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        answer = qa_chain.run(request.question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        return {"error": str(e)}
```

**Diferencias con el Servicio Principal**:
- **Salida Extendida**: Incluye pregunta original en la respuesta
- **Manejo de Errores**: Captura y devuelve errores explícitamente
- **Procesamiento Directo**: Sin etapas intermedias

## Componentes Compartidos

### Configuración de Embeddings

```python
embedding_model = HuggingFaceEmbeddings(
    model_name="/app/local_models/all-MiniLM-L6-v2"
)
```

**Características del Modelo**:
- **Modelo Local**: Almacenado en contenedor
- **Dimensiones**: 384 vectores
- **Optimización**: Balance entre calidad y velocidad
- **Multilingüe**: Soporte para español

### Conexión a Qdrant

```python
vector_store = Qdrant.from_existing_collection(
    collection_name="corpus_gecko3",
    url=QDRANT_HOST,
    embedding=embedding_model,
    timeout=600.0
)
```

**Configuración**:
- **Colección Existente**: Utiliza datos pre-cargados
- **Timeout Extendido**: 10 minutos para operaciones largas
- **URL Configurable**: Endpoint definido por variable de entorno

### Modelo de Lenguaje

```python
llm = ChatOllama(model="llama3", base_url=OLLAMA_HOST)
```

**Características**:
- **Modelo Local**: Llama3 ejecutándose en Ollama
- **Chat Interface**: Optimizado para conversaciones
- **Configuración Flexible**: URL configurable por entorno

### Configuración CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Configuración Permisiva**:
- **Orígenes**: Permite todos los orígenes (desarrollo)
- **Métodos**: Todos los métodos HTTP
- **Headers**: Todos los headers permitidos
- **Credenciales**: Soporte para autenticación

## Variables de Entorno

### Configuración de Servicios

```python
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://qdrant:6333")
```

**Variables Soportadas**:
- **OLLAMA_HOST**: Endpoint del servicio Ollama
- **QDRANT_HOST**: Endpoint de la base de datos vectorial

**Valores por Defecto**:
- Configurados para entorno Docker Compose
- Utilizan nombres de servicios como hostnames
- Puertos estándar para cada servicio

## Comparación de Servicios

### Servicio Principal (Puerto 8000)

**Ventajas**:
- **Análisis Inteligente**: Determina automáticamente la sección relevante
- **Búsqueda Optimizada**: Filtrado por tipo de documento
- **Respuestas Precisas**: Contexto más específico y relevante
- **Extensibilidad**: Fácil adición de nuevas etapas de procesamiento

**Casos de Uso Ideales**:
- Consultas específicas sobre temas técnicos
- Preguntas que requieren análisis de dominio
- Búsquedas en documentación estructurada
- Aplicaciones que requieren alta precisión

### Servicio QA (Puerto 8002)

**Ventajas**:
- **Velocidad**: Procesamiento más rápido
- **Simplicidad**: Menos puntos de fallo
- **Cobertura Amplia**: Busca en todo el corpus
- **Compatibilidad**: Interfaz estándar de QA

**Casos de Uso Ideales**:
- Consultas generales y exploratorias
- Búsquedas rápidas de información
- Aplicaciones que priorizan velocidad sobre precisión
- Prototipado y desarrollo inicial

## Monitoreo y Debugging

### Logging y Diagnóstico

Ambos servicios incluyen:
- **Logs de Contenedor**: Salida estándar de Docker
- **Manejo de Excepciones**: Captura de errores detallada
- **Métricas de Rendimiento**: Tiempo de respuesta implícito

### Herramientas de Testing

Scripts de prueba disponibles en `/test/`:
- **Consultas de Ejemplo**: Preguntas predefinidas para testing
- **Diferentes Tipos**: Consultas simples y complejas
- **Validación de Endpoints**: Verificación de ambos servicios

## Optimizaciones de Rendimiento

### Caching y Reutilización

- **Modelos Cargados**: Embeddings y LLM cargados una vez
- **Conexiones Persistentes**: Reutilización de conexiones a bases de datos
- **Vectores Pre-calculados**: Embeddings almacenados en Qdrant

### Configuración de Recursos

- **Timeouts Apropiados**: Configuración para operaciones largas
- **Límites de Memoria**: Gestión eficiente de recursos
- **Concurrencia**: FastAPI maneja múltiples peticiones simultáneas
