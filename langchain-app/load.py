from gecko_client import GECOClient

from typing import Literal

from langchain_ollama import OllamaEmbeddings

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_community.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings

import unicodedata
import re

from langchain.schema import Document
from langchain_ollama import ChatOllama
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import Annotated, List, TypedDict

from langchain.schema import Document
import json
import os

docs = []
host = "qdrant"
#embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
embedding_model = HuggingFaceEmbeddings(
    model_name="./local_models/all-MiniLM-L6-v2"
)
# Connect to remote Qdrant
qdrant = QdrantClient(
    host=host,  # Replace with actual IP or domain
    port=6333,
    https=False
)

collection_name = "corpus_gecko3"
# Delete if exists (optional - if you want to recreate every time)
if qdrant.collection_exists(collection_name=collection_name):
    qdrant.delete_collection(collection_name=collection_name)
    print("colection deleted: ", collection_name)
qdrant.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)


client = GECOClient("usuario_anonimo", "2024anonimo")
client.get_token()

corpus_response = client.list_corpus()
corpus_data = corpus_response.json()["data"]["proyectos"]

def split_text_into_chunks(text, chunk_size):
    """
    Splits text into chunks of fixed integer size and includes leftover characters in the final chunk.
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

# Iterate through each corpus and enrich it with documents
corpus_count = str(len(corpus_data))
for j,corpus in enumerate(corpus_data):
    corpus_id = str(corpus["id"])
    corpus_name = str(corpus["nombre"])
    #print("Corpus " + corpus_id + " (" + str(j+1) + " of " + corpus_count + ")")
    docs = []

    try:
        doc_response = client.list_corpus_documents(corpus_id=corpus_id)
        if doc_response.status_code == 200:
            doc_data = doc_response.json().get("data", [])
            docs_count = str(len(doc_data))
            if len(doc_data) > 0:
                for i, document in enumerate(doc_data):
                    #print("Corpus " + corpus_id + " (" + str(j+1) + " of " + corpus_count + ")" + " - Document " + str(document['id']) + " (" + str(i+1) + " of " + docs_count + ")")
                    #print( str(corpus_id) + ' - ' + str(document['id']) + ' - ' + str(document['derechos']))
                    if document['derechos'] is False:
                        response = client.get_corpus_text(corpus_id = str(corpus_id), documents_id = str(document['id']))
                        text = response['data']
                        document['archivo'] = re.sub(r'[()\s]', lambda m: '_' if m.group(0) == ' ' else '', 
                            unicodedata.normalize('NFKD', document['archivo'])
                            .encode('ascii', 'ignore')
                            .decode('utf-8')
                        )
                        #if len(text) > 1500:
                        #    chunks = split_text_into_chunks(text, 1500)
                        #    for k, chunk in enumerate(chunks):
                        #        #docs.append(Document(page_content=chunk, metadata=metadata))
                        #        #print("Corpus " + corpus_id + " (" + str(j+1) + " of " + corpus_count + ")" + " - Document " + str(document['id']) + " (" + str(i+1) + " of " + docs_count + ")")
                        #        docs.append(Document(page_content=chunk, metadata={"source": str(document['archivo']), "corpus_id": str(corpus_id), "corpus_name": corpus_name, "document": str(document['id']), "chunk": str(k+1)}))
                        #else:
                            #docs.append(Document(page_content=text, metadata=metadata))
                        docs.append(Document(page_content=response["data"], metadata={"source": str(document['archivo']), "corpus_id": str(corpus_id), "corpus_name": corpus_name, "document": str(document['id']), "chunk": '1'}))
            #print("Corpus " + corpus_id + " (" + str(j+1) + " of " + corpus_count + ")" + " - Document " + str(document['id']) + " (" + str(i+1) + " of " + docs_count + ")")            
            corpus["documents"] = doc_data
        else:
            corpus["documents"] = []

    except Exception as e:
        print(f"Failed to fetch documents for corpus {corpus_id}: {e}")
        corpus["documents"] = []

    text_length = len(response["data"])
    if len(docs) > 0:
        print("Corpus id: ", str(corpus_id))
        print("Text Document Size: ", text_length)
        print("Number of Docs: ", str(len(docs)))
        # print(docs[0])
        splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        split_docs = splitter.split_documents(docs)
        # Create vector store
        print("embedding")    
        vector_store = Qdrant.from_documents(
            documents=split_docs,
            embedding=embedding_model,
            location="http://" + host + ":6333",
            collection_name=collection_name,
        )
        #vector_store = InMemoryVectorStore(llm)
        _ = vector_store.add_documents(split_docs)
        #print("Document added: ", corpus_id)
#        print("Example: ", docs[0])

# Now `corpus_data` has each corpus with its documents attached

#print(corpus_data)
#with open("corpus_with_documents.json", "w", encoding="utf-8") as f:
#    json.dump(corpus_data, f, ensure_ascii=False, indent=2)

#print("✅ Output written to 'corpus_with_documents.json'")
