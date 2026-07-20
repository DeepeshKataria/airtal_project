"""
Unit and Integration Tests for Phase 2 (RAG Core)
"""

import os
import pytest
from src.rag.vectorstore import get_embeddings, get_or_build_vectorstore, CHROMA_DB_DIR
from src.rag.retriever import AirtelRetriever, retrieve_similar_chunks

def test_embeddings_initialization():
    embeddings = get_embeddings()
    query_vector = embeddings.embed_query("Airtel SD-WAN pitch")
    assert isinstance(query_vector, list)
    assert len(query_vector) == 384  # BAAI/bge-small-en-v1.5 dimension

def test_vectorstore_indexing():
    vectorstore = get_or_build_vectorstore()
    count = vectorstore._collection.count()
    assert count > 0
    assert os.path.exists(CHROMA_DB_DIR)

def test_retriever_query_relevance():
    retriever = AirtelRetriever()
    results = retriever.retrieve("How do I pitch Airtel Managed SD-WAN?", k=3)
    assert len(results) > 0
    
    first_result = results[0]
    assert "text" in first_result
    assert "source_url" in first_result
    assert "score" in first_result
    assert len(first_result["text"]) > 0
    
    # Check relevance of top chunk text
    text_content = first_result["text"].lower()
    assert "sd-wan" in text_content or "network" in text_content or "airtel" in text_content
