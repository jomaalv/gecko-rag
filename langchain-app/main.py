from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_core.documents import Document
#from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware


# Your RAG logic imports here
# ✅ Use new langchain-ollama
#from langchain_ollama import OllamaLLM
from langchain_ollama import ChatOllama
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from langchain import hub
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict, Annotated, Literal, List

import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://qdrant:6333")



# ==== Setup ====

embedding_model = HuggingFaceEmbeddings(model_name="/app/local_models/all-MiniLM-L6-v2")

vector_store = Qdrant.from_existing_collection(
    collection_name="corpus_gecko3",
    url=QDRANT_HOST,
    embedding=embedding_model,
    timeout=600.0
)

#llm = ChatOllama(model="llama3")
llm = ChatOllama(model="llama3", base_url=OLLAMA_HOST)
#llm = Ollama(model="llama3", base_url=OLLAMA_HOST)
#llm = OllamaLLM(model="llama3", base_url=OLLAMA_HOST)
prompt = hub.pull("rlm/rag-prompt")

class Search(TypedDict):
    query: Annotated[str, ..., "Search query to run."]
    section: Annotated[
        Literal["Aprendiendo sobre el Método de los Elementos Finitos.txt", "MTDs.txt", "AME1CO.txt", "AME1CR.txt", "AME1JN.txt"],
        ..., "Section to query."
    ]

class State(TypedDict):
    question: str
    query: Search
    context: List[Document]
    answer: str

def analyze_query(state: State):
    structured_llm = llm.with_structured_output(Search)
    query = structured_llm.invoke(state["question"])
    return {"query": query}

def retrieve(state: State):
    query = state["query"]
    retrieved_docs = vector_store.similarity_search(
        query["query"], k=5,
        filter={"source": query["section"]}
    )
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

graph_builder = StateGraph(State).add_sequence([analyze_query, retrieve, generate])
graph_builder.add_edge(START, "analyze_query")
graph = graph_builder.compile()

app = FastAPI()
class Question(BaseModel):
    question: str

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    steps = graph.invoke({"question": request.question})
    return {"answer": steps["answer"]}

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
