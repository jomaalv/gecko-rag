from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOllama

import os

# ==== Configuration ====
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://qdrant:6333")

# ==== FastAPI setup ====
app = FastAPI()

# ✅ Allow CORS from all origins (adjust if needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for Flutter web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==== Request Schema ====
class QuestionRequest(BaseModel):
    question: str

# ==== Embedding and Vector Store ====
embedding = HuggingFaceEmbeddings(model_name="/app/local_models/all-MiniLM-L6-v2")

qdrant = QdrantClient(
    url=QDRANT_HOST,  # or remote URL
)
vectorstore = Qdrant(
    client=qdrant,
    collection_name="corpus_gecko3",  # <- replace with your collection name
    embeddings=embedding,
)


# ==== LLM (Ollama) ====
llm = ChatOllama(model="llama3", base_url=OLLAMA_HOST)

# ==== QA Chain ====
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"  # Fastest; use "refine" if quality > speed
)
app = FastAPI()
# ==== Endpoint ====
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        answer = qa_chain.run(request.question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        return {"error": str(e)}
    
# ==== FastAPI setup ==== #
#app = FastAPI()
# ✅ Allow CORS from all origins (or just your Flutter web origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)