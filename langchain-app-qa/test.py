from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_ollama import ChatOllama  # or ChatOpenAI
from qdrant_client import QdrantClient

OLLAMA_HOST = "http://ollama:11434"
QDRANT_HOST = "http://qdrant:6333"

# 1. Load LLM (local Ollama or OpenAI)
llm = ChatOllama(model="llama3", base_url=OLLAMA_HOST)

# 2. Create Qdrant client
qdrant = QdrantClient(
    url=QDRANT_HOST,  # or remote URL
)

# 3. Create embedding model (same one used to populate Qdrant)
embedding = HuggingFaceEmbeddings(model_name="/app/local_models/all-MiniLM-L6-v2")

# 4. Load full collection from Qdrant
vectorstore = Qdrant(
    client=qdrant,
    collection_name="corpus_gecko3",  # <- replace with your collection name
    embeddings=embedding,
)

# 5. Make a retriever (search across all docs)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# 6. Wrap in a RetrievalQA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="refine"  # or "map_reduce" if long context
)

# 7. Query it
question = "Que se refiere a la división de un medio continuo en un conjunto de pequeños elementos interconectados por una serie de puntos llamados nodos?"
question = "que ecuaciones diferenciales están entre las más complejas de resolver teórica o numéricamente?"
#print("---- Scores ----")
#docs_with_scores = vectorstore.similarity_search_with_score(question, k=5)
#docs_with_scores = vectorstore.similarity_search_with_score(question, k=5)
#for i, (doc, score) in enumerate(docs_with_scores):
#    print(f"\nDoc #{i+1} - Cosine Similarity Score: {score:.4f}")
#    print("Content:", doc.page_content[:500])
#    print("Metadata:", doc.metadata)

# Retrieve documents manually
docs = retriever.get_relevant_documents(question)

# Deduplicate by metadata field (e.g., 'document' or '_id')
unique_docs = {}
for doc in docs:
    doc_id = doc.metadata.get('document')  # or use '_id'
    if doc_id not in unique_docs:
        unique_docs[doc_id] = doc

# Display deduplicated documents
for i, doc in enumerate(unique_docs.values()):
    print(f"\nDoc #{i+1}")
    print("Content:", doc.page_content[:500])
    print("Metadata:", doc.metadata)

# Print each retrieved document (and optional metadata)
#print("---- Retrieved Documents ----")
#for i, doc in enumerate(docs):
#    print(f"\nDoc #{i+1}")
#    print("Content:", doc.page_content[:500])  # Show first 500 chars
#    print("Metadata:", doc.metadata)

# Then pass manually to the chain
response = qa.combine_documents_chain.run(input_documents=list(unique_docs.values()), question=question)
print("----response-----")
print(response)
