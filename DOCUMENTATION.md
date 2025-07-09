# Gecko RAG - Comprehensive Documentation

## Project Overview

Gecko RAG is a Retrieval-Augmented Generation (RAG) system designed to provide intelligent question-answering capabilities over academic and technical documents. The system integrates multiple technologies to create a complete AI-powered document search and response platform.

## Architecture

The project follows a microservices architecture with the following components:

### Core Components

1. **LangChain Backend Services** (2 variants)
2. **Flutter Web Frontend**
3. **Vector Database (Qdrant)**
4. **Language Model (Ollama with Llama3)**
5. **GECO API Client**

## System Components

### 1. LangChain Backend (`langchain-app/`)

**Purpose**: Primary RAG service with advanced query analysis and structured retrieval

**Key Features**:
- **Structured Query Analysis**: Uses LangGraph to analyze incoming questions and determine the appropriate document section to search
- **Multi-step Processing Pipeline**:
  - Query analysis and categorization
  - Document retrieval with filtering
  - Response generation
- **Document Filtering**: Supports filtering by specific document sections:
  - `aprendiendo_sobre_el_metodo_de_los_elementos_finitos.txt`
  - `mtds.txt`
  - `ame1co.txt`
  - `ame1cr.txt`
  - `ame1jn.txt`

**Technical Stack**:
- FastAPI for REST API
- LangChain for RAG pipeline
- LangGraph for workflow orchestration
- HuggingFace embeddings (all-MiniLM-L6-v2)
- Qdrant for vector storage
- Ollama/Llama3 for language generation

**API Endpoints**:
- `POST /ask`: Submit questions for intelligent analysis and response
  - Input: `{"question": "your question here"}`
  - Output: `{"answer": "generated response"}`

**Port**: 8000

### 2. LangChain QA Backend (`langchain-app-qa/`)

**Purpose**: Simplified QA service for direct question-answering without query analysis

**Key Features**:
- **Direct Retrieval**: Simple similarity search without query categorization
- **RetrievalQA Chain**: Uses LangChain's built-in QA chain for faster responses
- **Broader Search**: Searches across all documents without filtering

**Technical Stack**:
- FastAPI for REST API
- LangChain RetrievalQA
- Same embedding and vector store setup as main backend

**API Endpoints**:
- `POST /ask`: Submit questions for direct QA
  - Input: `{"question": "your question here"}`
  - Output: `{"question": "original question", "answer": "generated response"}`

**Port**: 8002

### 3. Flutter Web Frontend (`flutter-web/`)

**Purpose**: User interface for interacting with the RAG system

**Key Features**:
- Web-based chat interface
- Real-time communication with backend services
- Responsive design for various screen sizes
- Built and served as static files through Nginx

**Deployment**:
- Built Flutter web application
- Served via Nginx on port 80 (mapped to host port 8081)
- Static file serving with optimized performance

**Port**: 8081 (external), 80 (internal)

### 4. Vector Database (Qdrant)

**Purpose**: High-performance vector storage and similarity search

**Configuration**:
- Collection name: `corpus_gecko3`
- Vector dimensions: 384 (matching HuggingFace embeddings)
- Distance metric: Cosine similarity
- Persistent storage with Docker volumes

**Port**: 6333

### 5. Language Model (Ollama)

**Purpose**: Local language model serving for text generation

**Features**:
- **Multi-platform Support**:
  - CPU-only deployment
  - NVIDIA GPU acceleration
  - AMD GPU (ROCm) support
- **Model**: Llama3
- **Automatic Model Download**: Container automatically pulls Llama3 model on startup

**Ports**: 11435 (external), 11434 (internal)

### 6. GECO API Client (`gecko_client.py`)

**Purpose**: Interface for accessing external GECO document corpus

**Functionality**:
- **Authentication**: Token-based authentication with GECO API
- **Corpus Management**:
  - List available document corpora
  - Retrieve corpus metadata
  - Access corpus documents and applications
- **Document Processing**:
  - Extract text content from documents
  - Handle file attachments
  - Process document metadata

**Key Methods**:
- `get_token()`: Authenticate and retrieve access token
- `list_corpus()`: Get available document collections
- `list_corpus_documents()`: Retrieve documents from specific corpus
- `get_corpus_text()`: Extract text content from documents

## Data Processing Pipeline

### Document Loading Process (`load.py`)

**Purpose**: Populate the vector database with processed documents from GECO API

**Process Flow**:
1. **Authentication**: Connect to GECO API and obtain access token
2. **Corpus Discovery**: Retrieve list of available document corpora
3. **Document Processing**:
   - Iterate through each corpus
   - Extract documents with appropriate permissions
   - Clean and normalize document metadata
   - Process text content
4. **Text Chunking**: Split large documents using RecursiveCharacterTextSplitter
   - Chunk size: 1500 characters
   - Overlap: 200 characters
5. **Embedding Generation**: Create vector embeddings using HuggingFace model
6. **Vector Storage**: Store embeddings in Qdrant with metadata

**Document Metadata**:
- Source filename (normalized)
- Corpus ID and name
- Document ID
- Chunk number

## Deployment and Infrastructure

### Docker Compose Configuration

**Services Orchestration**:
- **Networks**: Custom `demo` network for inter-service communication
- **Volumes**: Persistent storage for Ollama models and Qdrant data
- **Profiles**: Support for different hardware configurations (CPU, GPU-NVIDIA, GPU-AMD)

**Environment Variables**:
- `OLLAMA_HOST`: Ollama service endpoint
- `QDRANT_HOST`: Qdrant service endpoint

**Service Dependencies**:
- Frontend depends on backend services
- Backend services depend on Qdrant and Ollama
- Automatic model initialization on startup

### Hardware Profiles

1. **CPU Profile** (`cpu`):
   - Standard CPU-only deployment
   - Suitable for development and light usage

2. **NVIDIA GPU Profile** (`gpu-nvidia`):
   - GPU acceleration for faster inference
   - Requires NVIDIA Docker runtime

3. **AMD GPU Profile** (`gpu-amd`):
   - AMD ROCm support for AMD GPUs
   - Uses specialized Ollama ROCm image

## API Usage Examples

### Testing the System

The project includes test scripts (`test/questions.bash`) with example queries:

```bash
# Basic question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Que es intestino?"}'

# Technical question about Finite Element Method
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Que me puedes decir del Método de los Elementos Finitos?"}'

# Complex mathematical question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "que ecuaciones diferenciales están entre las más complejas de resolver teórica o numéricamente?"}'
```

## Key Features and Capabilities

### Advanced RAG Pipeline
- **Intelligent Query Routing**: Automatically determines which document sections are most relevant
- **Multi-step Processing**: Query analysis → Document retrieval → Response generation
- **Contextual Understanding**: Maintains context throughout the conversation

### Scalable Architecture
- **Microservices Design**: Independent, scalable components
- **Container Orchestration**: Easy deployment and scaling with Docker Compose
- **Hardware Flexibility**: Support for various hardware configurations

### Document Processing
- **Automated Ingestion**: Connects to external document APIs
- **Intelligent Chunking**: Optimized text segmentation for better retrieval
- **Metadata Preservation**: Maintains document structure and relationships

### Performance Optimization
- **Vector Search**: High-performance similarity search with Qdrant
- **Local LLM**: Reduced latency with local language model deployment
- **Caching**: Persistent storage for models and embeddings

## Development and Maintenance

### Requirements Management
- Python dependencies managed via `requirements.txt`
- Consistent versions across all backend services
- Docker-based deployment eliminates environment issues

### Monitoring and Debugging
- **Service Health**: Docker Compose health checks and restart policies
- **API Testing**: Included test scripts for validation
- **Logging**: Container-based logging for troubleshooting

### Extensibility
- **Modular Design**: Easy to add new document sources or processing steps
- **API Compatibility**: RESTful APIs for integration with other systems
- **Model Flexibility**: Support for different language models and embedding models

## Security Considerations

### Authentication
- Token-based authentication for external API access
- Secure credential management through environment variables

### Network Security
- Internal Docker network isolation
- Controlled port exposure
- CORS configuration for web frontend

### Data Privacy
- Local deployment option for sensitive documents
- No external API calls for core RAG functionality
- Configurable data retention policies

## Performance Characteristics

### Response Times
- **Simple QA**: ~2-5 seconds (langchain-app-qa)
- **Advanced Analysis**: ~5-10 seconds (langchain-app)
- **Document Loading**: Varies by corpus size

### Resource Requirements
- **CPU**: Minimum 4 cores recommended
- **Memory**: 8GB+ RAM for optimal performance
- **Storage**: Depends on document corpus size
- **GPU**: Optional but recommended for faster inference

## Future Enhancements

### Potential Improvements
- **Multi-language Support**: Extend to other languages beyond Spanish
- **Advanced Analytics**: Query analytics and usage patterns
- **Real-time Updates**: Live document synchronization
- **Enhanced UI**: More sophisticated web interface
- **API Versioning**: Support for multiple API versions
- **Batch Processing**: Bulk document processing capabilities

This documentation provides a comprehensive overview of the Gecko RAG system, covering all major components, functionality, and operational aspects of the platform.
