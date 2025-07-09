# Gecko RAG - Resumen General del Proyecto

## Descripción del Proyecto

Gecko RAG es un sistema de Generación Aumentada por Recuperación (RAG) diseñado para proporcionar capacidades inteligentes de preguntas y respuestas sobre documentos académicos y técnicos. El sistema integra múltiples tecnologías para crear una plataforma completa de búsqueda y respuesta de documentos impulsada por IA.

## Arquitectura General

El proyecto sigue una arquitectura de microservicios con los siguientes componentes principales:

### Componentes Principales

1. **Servicios Backend de LangChain** (2 variantes)
2. **Frontend Web en Flutter**
3. **Base de Datos Vectorial (Qdrant)**
4. **Modelo de Lenguaje (Ollama con Llama3)**
5. **Cliente API GECO**

## Arquitectura del Sistema

![Diagrama de Arquitectura Docker](./diagram.png)

El diagrama muestra la arquitectura completa del sistema con todos los contenedores Docker y sus interacciones:

### Componentes Visualizados:
- **Flutter Frontend** (puerto 80/TCP) - Interfaz web de usuario
- **LangChain Backend Principal** (puerto 8000/TCP) - Servicio RAG avanzado con all-MiniLM-L6-v2
- **LangChain Backend QA** (puerto 8002/TCP) - Servicio QA simplificado con all-MiniLM-L6-v2
- **Ollama** (puerto 11435/TCP) - Servidor de modelo de lenguaje Llama3
- **Qdrant** (puerto 6333/TCP) - Base de datos vectorial

### Flujo de Comunicación:
```
[Usuario] → [Flutter:80] → [LangChain:8000/8002] → [Ollama:11435] (Generación)
                                    ↓
                              [Qdrant:6333] (Búsqueda Vectorial)
```

## Flujo de Trabajo del Sistema

```
[Documentos GECO] → [Cliente GECO] → [Procesamiento] → [Embeddings] → [Qdrant]
                                                                           ↓
[Usuario] → [Frontend Flutter] → [Backend LangChain] → [Consulta Vectorial] → [Respuesta]
```

## Características Principales

### Pipeline RAG Avanzado
- **Enrutamiento Inteligente de Consultas**: Determina automáticamente qué secciones de documentos son más relevantes
- **Procesamiento Multi-etapa**: Análisis de consulta → Recuperación de documentos → Generación de respuesta
- **Comprensión Contextual**: Mantiene el contexto a lo largo de la conversación

### Arquitectura Escalable
- **Diseño de Microservicios**: Componentes independientes y escalables
- **Orquestación de Contenedores**: Despliegue y escalado fácil con Docker Compose
- **Flexibilidad de Hardware**: Soporte para varias configuraciones de hardware

### Procesamiento de Documentos
- **Ingesta Automatizada**: Se conecta a APIs de documentos externos
- **Segmentación Inteligente**: Segmentación de texto optimizada para mejor recuperación
- **Preservación de Metadatos**: Mantiene la estructura y relaciones de documentos

## Puertos y Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Backend Principal | 8000 | Servicio RAG avanzado con análisis de consultas |
| Backend QA | 8002 | Servicio QA simplificado |
| Frontend Flutter | 8081 | Interfaz web de usuario |
| Qdrant | 6333 | Base de datos vectorial |
| Ollama | 11435 | Servidor de modelo de lenguaje |

## Tecnologías Utilizadas

- **Python**: Backend y procesamiento de datos
- **FastAPI**: APIs REST
- **LangChain**: Pipeline RAG
- **LangGraph**: Orquestación de flujos de trabajo
- **Flutter**: Frontend web
- **Qdrant**: Base de datos vectorial
- **Ollama/Llama3**: Modelo de lenguaje local
- **HuggingFace**: Modelos de embeddings
- **Docker**: Contenedorización y despliegue

## Casos de Uso

1. **Consultas Académicas**: Búsqueda en documentos técnicos y académicos
2. **Análisis de Métodos Numéricos**: Especializado en elementos finitos y ecuaciones diferenciales
3. **Investigación Documental**: Exploración inteligente de corpus de documentos
4. **Asistencia Educativa**: Apoyo en el aprendizaje de conceptos técnicos

## Ventajas del Sistema

- **Despliegue Local**: No dependencia de servicios externos para el procesamiento principal
- **Multilingüe**: Optimizado para contenido en español
- **Escalable**: Arquitectura preparada para crecimiento
- **Flexible**: Soporte para diferentes configuraciones de hardware
- **Seguro**: Procesamiento local de documentos sensibles
