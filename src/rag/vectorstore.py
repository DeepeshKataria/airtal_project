"""
ChromaDB Vector Store Manager for Airtel B2B AI Assistant
Handles embedding generation (BAAI/bge-small-en-v1.5) and vector store persistence.
"""

import os
import json
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CHROMA_DB_DIR = os.path.join(PROJECT_ROOT, "chroma_db")
PROCESSED_CHUNKS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "chunks.json")
COLLECTION_NAME = "airtel_b2b_docs"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

_embeddings_instance = None

def get_embeddings():
    """Return the shared HuggingFace embedding model instance (singleton pattern)."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings_instance

def load_processed_chunks() -> List[Document]:
    if not os.path.exists(PROCESSED_CHUNKS_FILE):
        raise FileNotFoundError(f"Processed chunks file not found at {PROCESSED_CHUNKS_FILE}. Run Phase 1 ingest first.")
        
    with open(PROCESSED_CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)
        
    documents = []
    for item in chunks_data:
        doc = Document(
            page_content=item.get("text", ""),
            metadata={
                "source_url": item.get("source_url", ""),
                "file_name": item.get("file_name", ""),
                "chunk_id": item.get("id", ""),
                "chunk_index": item.get("chunk_index", 0)
            }
        )
        documents.append(doc)
    return documents

def get_or_build_vectorstore(force_rebuild: bool = False) -> Chroma:
    """
    Return an existing ChromaDB vector store or build one from processed chunks.

    If the vector store already exists on disk and contains documents, it is reused.
    Otherwise (or if force_rebuild=True), it is rebuilt from data/processed/chunks.json.
    """
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    embeddings = get_embeddings()
    
    if not force_rebuild and os.path.exists(CHROMA_DB_DIR) and len(os.listdir(CHROMA_DB_DIR)) > 0:
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME
        )
        if vectorstore._collection.count() > 0:
            return vectorstore
            
    # Clear existing Chroma DB collection on rebuild
    if os.path.exists(CHROMA_DB_DIR):
        try:
            existing_vs = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=embeddings,
                collection_name=COLLECTION_NAME
            )
            existing_vs.delete_collection()
        except Exception:
            pass
            
    documents = load_processed_chunks()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR,
        collection_name=COLLECTION_NAME
    )
    return vectorstore

if __name__ == "__main__":
    vs = get_or_build_vectorstore(force_rebuild=True)
    print(f"Vector store successfully initialized with {vs._collection.count()} document embeddings in {CHROMA_DB_DIR}")
