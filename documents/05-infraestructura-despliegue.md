# Infraestructura y Despliegue - Documentación Técnica

## Descripción General

El sistema Gecko RAG utiliza Docker Compose para orquestar múltiples servicios que trabajan en conjunto para proporcionar capacidades de RAG (Retrieval-Augmented Generation). La arquitectura está diseñada para ser escalable, mantenible y compatible con diferentes configuraciones de hardware.

## Diagrama de Arquitectura

![Diagrama de Arquitectura Docker](./diagram.png)

El diagrama ilustra la arquitectura completa del sistema mostrando:

### Contenedores y Puertos:
- **flutter-frontend**: Puerto 80 (TCP) - Interfaz web servida por Nginx
- **langchain-backend**: Puerto 8000 (TCP) - Servicio RAG principal con análisis inteligente
- **langchain-backend-qa**: Puerto 8002 (TCP) - Servicio QA simplificado
- **ollama**: Puerto 11435 (TCP) - Servidor Llama3 para generación de texto
- **qdrant**: Puerto 6333 (TCP) - Base de datos vectorial para búsqueda semántica

### Modelos Integrados:
- **all-MiniLM-L6-v2**: Modelo de embeddings (384 dimensiones) en ambos backends
- **Llama3**: Modelo de lenguaje para generación de respuestas

### Comunicación Entre Servicios:
- **HTTP/TCP**: Protocolo de comunicación entre todos los servicios
- **Red Interna Docker**: Comunicación segura entre contenedores
- **Resolución DNS**: Nombres de servicios como hostnames internos

### Flujo de Datos Según el Diagrama:

1. **Usuario → Flutter Frontend (puerto 80)**
   - Interfaz web accesible desde el navegador
   - Servida por Nginx como contenedor estático

2. **Frontend → Backends (puertos 8000/8002)**
   - Peticiones HTTP POST a `/ask` endpoint
   - Comunicación JSON para preguntas y respuestas

3. **Backends → Qdrant (puerto 6333)**
   - Búsqueda de similitud vectorial
   - Filtrado por metadatos de documentos
   - Recuperación de contexto relevante

4. **Backends → Ollama (puerto 11435)**
   - Generación de respuestas con modelo Llama3
   - Procesamiento de prompts con contexto recuperado

5. **Modelos Integrados:**
   - **all-MiniLM-L6-v2**: Embeddings en ambos backends
   - **Llama3**: Generación de lenguaje natural en Ollama

## Arquitectura de Contenedores

### Servicios Principales

```yaml
services:
  langchain-backend:      # Puerto 8000 - Servicio RAG avanzado
  langchain-backend-qa:   # Puerto 8002 - Servicio QA simplificado  
  flutter-frontend:       # Puerto 8081 - Interfaz web
  qdrant:                # Puerto 6333 - Base de datos vectorial
  ollama-cpu/gpu:        # Puerto 11435 - Modelo de lenguaje
```

### Red y Comunicación

```yaml
networks:
  demo:
```

**Características de la Red**:
- **Red Interna**: Comunicación segura entre contenedores
- **Aislamiento**: Separación del tráfico externo
- **Resolución DNS**: Nombres de servicios como hostnames
- **Configuración Simplificada**: Una sola red para todos los servicios

### Volúmenes Persistentes

```yaml
volumes:
  ollama_storage:    # Almacenamiento de modelos Ollama
  qdrant_storage:    # Base de datos vectorial persistente
```

**Beneficios del Almacenamiento Persistente**:
- **Persistencia de Datos**: Los datos sobreviven a reinicios de contenedores
- **Optimización**: Evita re-descarga de modelos en cada inicio
- **Backup**: Facilita respaldo de datos importantes
- **Escalabilidad**: Permite migración de datos entre entornos

## Configuración de Servicios

### Backend LangChain Principal

```yaml
langchain-backend:
  build: ./langchain-app
  container_name: langchain-backend
  networks: ['demo']
  restart: unless-stopped
  environment:
    - OLLAMA_HOST=http://ollama:11434
    - QDRANT_HOST=http://qdrant:6333
  ports:
    - "8000:8000"
  depends_on:
    - qdrant
    - ollama-cpu
```

**Características de Configuración**:
- **Build Local**: Construye imagen desde código fuente
- **Variables de Entorno**: Configuración de endpoints de servicios
- **Dependencias**: Espera a que Qdrant y Ollama estén listos
- **Reinicio Automático**: Se reinicia automáticamente si falla

### Backend QA

```yaml
langchain-backend-qa:
  build: ./langchain-app-qa
  container_name: langchain-backend-qa
  networks: ['demo']
  restart: unless-stopped
  environment:
    - OLLAMA_HOST=http://ollama:11434
    - QDRANT_HOST=http://qdrant:6333
  ports:
    - "8002:8002"
  depends_on:
    - qdrant
    - ollama-cpu
```

**Diferencias con el Backend Principal**:
- **Puerto Diferente**: 8002 vs 8000
- **Código Base Separado**: Directorio `langchain-app-qa`
- **Mismas Dependencias**: Utiliza los mismos servicios base

### Frontend Flutter

```yaml
flutter-frontend:
  build: ./flutter-web
  container_name: flutter-frontend
  networks: ['demo']
  restart: unless-stopped
  ports:
    - "8081:80"
  depends_on:
    - langchain-backend
```

**Configuración del Frontend**:
- **Nginx**: Sirve aplicación Flutter compilada
- **Puerto 80 Interno**: Configuración estándar de Nginx
- **Puerto 8081 Externo**: Acceso desde el host
- **Dependencia Backend**: Espera al servicio principal

### Base de Datos Vectorial Qdrant

```yaml
qdrant:
  image: qdrant/qdrant
  hostname: qdrant
  container_name: qdrant
  networks: ['demo']
  restart: unless-stopped
  ports:
    - 6333:6333
  volumes:
    - qdrant_storage:/qdrant/storage
```

**Características de Qdrant**:
- **Imagen Oficial**: Utiliza imagen oficial de Qdrant
- **Almacenamiento Persistente**: Datos guardados en volumen
- **Puerto Estándar**: 6333 para API REST
- **Hostname Fijo**: Facilita resolución DNS interna

## Configuración Multi-Hardware

### Perfiles de Hardware

El sistema soporta tres configuraciones diferentes mediante perfiles de Docker Compose:

#### 1. Perfil CPU (`cpu`)

```yaml
ollama-cpu:
  profiles: ["cpu"]
  <<: *service-ollama

ollama-pull-llama-cpu:
  profiles: ["cpu"]
  <<: *init-ollama
  depends_on:
    - ollama-cpu
```

**Características**:
- **Solo CPU**: No requiere GPU
- **Compatibilidad Universal**: Funciona en cualquier sistema
- **Rendimiento Moderado**: Adecuado para desarrollo y pruebas
- **Recursos Mínimos**: Menor consumo de recursos

#### 2. Perfil GPU NVIDIA (`gpu-nvidia`)

```yaml
ollama-gpu:
  profiles: ["gpu-nvidia"]
  <<: *service-ollama
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

**Características**:
- **Aceleración GPU**: Utiliza CUDA para inferencia rápida
- **Requisitos**: NVIDIA Docker runtime
- **Alto Rendimiento**: Respuestas más rápidas
- **Recursos GPU**: Requiere GPU NVIDIA compatible

#### 3. Perfil GPU AMD (`gpu-amd`)

```yaml
ollama-gpu-amd:
  profiles: ["gpu-amd"]
  <<: *service-ollama
  image: ollama/ollama:rocm
  devices:
    - "/dev/kfd"
    - "/dev/dri"
```

**Características**:
- **ROCm Support**: Utiliza ROCm para GPUs AMD
- **Imagen Especializada**: Versión específica para AMD
- **Dispositivos**: Acceso directo a dispositivos AMD
- **Compatibilidad AMD**: Soporte para tarjetas AMD

### Plantillas de Servicio (YAML Anchors)

```yaml
x-ollama: &service-ollama
  image: ollama/ollama:latest
  container_name: ollama
  networks: ['demo']
  restart: unless-stopped
  ports:
    - 11435:11434
  volumes:
    - ollama_storage:/root/.ollama
```

**Ventajas de las Plantillas**:
- **Reutilización**: Configuración común para todos los perfiles
- **Mantenimiento**: Cambios centralizados
- **Consistencia**: Misma configuración base
- **Flexibilidad**: Personalización por perfil

### Inicialización Automática de Modelos

```yaml
x-init-ollama: &init-ollama
  image: ollama/ollama:latest
  networks: ['demo']
  container_name: ollama-pull-llama
  volumes:
    - ollama_storage:/root/.ollama
  entrypoint: /bin/sh
  environment:
    - OLLAMA_HOST=ollama:11434
  command:
    - "-c"
    - "sleep 3; ollama pull llama3"
```

**Proceso de Inicialización**:
1. **Espera**: Pausa 3 segundos para que Ollama esté listo
2. **Descarga**: Ejecuta `ollama pull llama3`
3. **Almacenamiento**: Guarda modelo en volumen persistente
4. **Terminación**: Contenedor se cierra tras completar descarga

## Comandos de Despliegue

### Despliegue con CPU

```bash
docker-compose --profile cpu up -d
```

**Servicios Iniciados**:
- langchain-backend
- langchain-backend-qa
- flutter-frontend
- qdrant
- ollama-cpu
- ollama-pull-llama-cpu

### Despliegue con GPU NVIDIA

```bash
docker-compose --profile gpu-nvidia up -d
```

**Requisitos Previos**:
- NVIDIA Docker runtime instalado
- GPU NVIDIA compatible
- Drivers NVIDIA actualizados

### Despliegue con GPU AMD

```bash
docker-compose --profile gpu-amd up -d
```

**Requisitos Previos**:
- ROCm instalado en el host
- GPU AMD compatible
- Dispositivos `/dev/kfd` y `/dev/dri` accesibles

## Configuración de Red y Puertos

### Mapeo de Puertos

| Servicio | Puerto Interno | Puerto Externo | Protocolo |
|----------|----------------|----------------|-----------|
| Backend Principal | 8000 | 8000 | HTTP |
| Backend QA | 8002 | 8002 | HTTP |
| Frontend Flutter | 80 | 8081 | HTTP |
| Qdrant | 6333 | 6333 | HTTP |
| Ollama | 11434 | 11435 | HTTP |

### Comunicación Interna

```
flutter-frontend:80 → langchain-backend:8000
langchain-backend:8000 → qdrant:6333
langchain-backend:8000 → ollama:11434
langchain-backend-qa:8002 → qdrant:6333
langchain-backend-qa:8002 → ollama:11434
```

## Gestión de Datos

### Volúmenes de Datos

#### Ollama Storage

```yaml
ollama_storage:/root/.ollama
```

**Contenido**:
- Modelos de lenguaje descargados (Llama3)
- Configuración de Ollama
- Cache de modelos
- Metadatos de modelos

**Tamaño Aproximado**: 4-8 GB (dependiendo del modelo)

#### Qdrant Storage

```yaml
qdrant_storage:/qdrant/storage
```

**Contenido**:
- Colección `corpus_gecko3`
- Vectores de embeddings (384 dimensiones)
- Metadatos de documentos
- Índices de búsqueda

**Tamaño**: Variable según corpus (típicamente 100MB-1GB)

### Backup y Restauración

#### Backup de Volúmenes

```bash
# Backup Qdrant
docker run --rm -v qdrant_storage:/data -v $(pwd):/backup alpine tar czf /backup/qdrant_backup.tar.gz -C /data .

# Backup Ollama
docker run --rm -v ollama_storage:/data -v $(pwd):/backup alpine tar czf /backup/ollama_backup.tar.gz -C /data .
```

#### Restauración de Volúmenes

```bash
# Restaurar Qdrant
docker run --rm -v qdrant_storage:/data -v $(pwd):/backup alpine tar xzf /backup/qdrant_backup.tar.gz -C /data

# Restaurar Ollama
docker run --rm -v ollama_storage:/data -v $(pwd):/backup alpine tar xzf /backup/ollama_backup.tar.gz -C /data
```

## Monitoreo y Logs

### Visualización de Logs

```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f langchain-backend

# Logs con timestamps
docker-compose logs -f -t
```

### Monitoreo de Estado

```bash
# Estado de servicios
docker-compose ps

# Uso de recursos
docker stats

# Información de volúmenes
docker volume ls
docker volume inspect gecko-rag-dev-v1_qdrant_storage
```

## Troubleshooting

### Problemas Comunes

#### 1. Ollama No Responde

```bash
# Verificar estado del contenedor
docker-compose ps ollama-cpu

# Verificar logs
docker-compose logs ollama-cpu

# Reiniciar servicio
docker-compose restart ollama-cpu
```

#### 2. Qdrant Sin Datos

```bash
# Verificar colección
curl http://localhost:6333/collections

# Verificar datos en colección
curl http://localhost:6333/collections/corpus_gecko3
```

#### 3. Backend No Conecta

```bash
# Verificar variables de entorno
docker-compose exec langchain-backend env | grep -E "(OLLAMA|QDRANT)"

# Probar conectividad interna
docker-compose exec langchain-backend ping qdrant
docker-compose exec langchain-backend ping ollama
```

### Comandos de Diagnóstico

```bash
# Información completa del sistema
docker-compose config

# Verificar red
docker network ls
docker network inspect gecko-rag-dev-v1_demo

# Verificar volúmenes
docker volume ls
docker volume inspect gecko-rag-dev-v1_ollama_storage
```

## Optimizaciones de Producción

### Configuraciones Recomendadas

#### 1. Límites de Recursos

```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

#### 2. Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

#### 3. Logging Configuration

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Seguridad

#### 1. Variables de Entorno Seguras

```bash
# Usar archivo .env
echo "OLLAMA_HOST=http://ollama:11434" > .env
echo "QDRANT_HOST=http://qdrant:6333" >> .env
```

#### 2. Red Personalizada

```yaml
networks:
  gecko-internal:
    driver: bridge
    internal: true
  gecko-external:
    driver: bridge
```

#### 3. Usuarios No-Root

```dockerfile
USER 1000:1000
```

## Escalabilidad

### Escalado Horizontal

```bash
# Múltiples instancias del backend
docker-compose up -d --scale langchain-backend=3
```

### Load Balancer

```yaml
nginx-lb:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - langchain-backend
```

### Configuración de Cluster

Para entornos de producción, considerar:
- **Docker Swarm**: Orquestación nativa de Docker
- **Kubernetes**: Orquestación avanzada con Helm charts
- **Consul/Nomad**: Stack de HashiCorp para servicios distribuidos
