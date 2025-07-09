# Gecko RAG - Resumen General del Proyecto

## ¿Qué es GECO?

GECO (Sistema de Gestión de Corpus) es la plataforma fundamental de gestión de corpus desarrollada por el Grupo de Ingeniería Lingüística del Instituto de Ingeniería de la UNAM (Universidad Nacional Autónoma de México). Este proyecto Gecko RAG extiende y potencia las capacidades de GECO mediante funcionalidades avanzadas de RAG (Generación Aumentada por Recuperación).

### Acerca del Sistema GECO

**GECO 3.0** es un sistema integral de gestión de corpus que sirve como plataforma centralizada para la investigación lingüística y el procesamiento de lenguaje natural. Proporciona:

**Funcionalidades Principales:**
- **Gestión de Corpus**: Sistema estructurado para organizar, almacenar y acceder a grandes colecciones de textos
- **Procesamiento de Documentos**: Herramientas para convertir y procesar varios formatos de documentos
- **Gestión de Usuarios**: Plataforma multiusuario con autenticación y control de acceso
- **Interfaz Web**: Acceso basado en navegador a recursos y herramientas de corpus


### Corpus Destacados en GECO

La plataforma GECO alberga diversos corpus lingüísticos incluyendo:

**Investigación Sociolingüística:**
- **Corpus Cempasúchil**: Conversaciones de WhatsApp de estudiantes de la UNAM (617 chats bilaterales de 2017)
- **Corpus del Habla de Sinaloa**: Documentación de dialectos regionales con análisis sociolingüístico

**Corpus de Dominios Especializados:**
- **Corpus de las Sexualidades de México (CSMX)**: Colección integral sobre terminología de sexualidad
- **Corpus Lingüístico en Ingeniería (CLI)**: Corpus en español enfocado en ingeniería
- **Corpus de medicina**: Terminología médica con más de 500,000 palabras

**Corpus Multilingües y Paralelos:**
- **Corpus de Contextos Definitorios**: Contextos definitorios en español-francés
- **Corpus paralelo de Biblias**: Textos bíblicos paralelos alineados a nivel de versículo

**Análisis de Redes Sociales y Sentimientos:**
- **SENT-COVID**: 4,986 tweets anotados para análisis de sentimientos sobre COVID-19
- **T-MexNeg**: 13,704 tweets en español mexicano con análisis de estructuras de negación
- **HeteroCorpus**: Tweets en inglés marcados para contenido heteronormativo

### Integración con Gecko RAG

Este proyecto Gecko RAG extiende las capacidades de GECO mediante:

**Búsqueda Mejorada**: Transición de búsqueda tradicional por palabras clave a búsqueda semántica por similitud usando embeddings vectoriales

**Respuestas Impulsadas por IA**: Adición de capacidades de generación de lenguaje natural para proporcionar respuestas contextuales en lugar de solo recuperación de documentos

**Análisis Avanzado**: Implementación de análisis inteligente de consultas para enrutar preguntas a las secciones de corpus más relevantes

**Interfaz Moderna**: Provisión de una interfaz web contemporánea construida con Flutter para una experiencia de usuario mejorada

**Arquitectura Escalable**: Despliegue en contenedores con arquitectura de microservicios para mejor escalabilidad y mantenimiento

La integración mantiene compatibilidad con la API existente de GECO mientras añade una poderosa capa RAG que transforma el acceso estático a corpus en un sistema interactivo e inteligente de consulta de documentos.

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
