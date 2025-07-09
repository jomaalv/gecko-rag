FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download embedding model directly during build
RUN pip install sentence-transformers && \
    python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').save('/app/local_models/all-MiniLM-L6-v2')"

# Copy your FastAPI app code
COPY . .
RUN apt update
RUN apt install -y nano

# Expose port and run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]