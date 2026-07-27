"""
Airtel B2B RAG Similarity Retriever
Implements top-k similarity search over ChromaDB vector store.
"""

from typing import List, Dict, Any
from src.rag.vectorstore import get_or_build_vectorstore

class AirtelRetriever:
    def __init__(self, vectorstore=None):
        self.vectorstore = vectorstore or get_or_build_vectorstore()
        
    def retrieve(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant document chunks for a given query with similarity scores.
        """
        if not query or not query.strip():
            return []
            
        results_with_scores = self.vectorstore.similarity_search_with_relevance_scores(query, k=k)
        retrieved_chunks = []
        
        for doc, score in results_with_scores:
            chunk_info = {
                "text": doc.page_content,
                "source_url": doc.metadata.get("source_url", "N/A"),
                "file_name": doc.metadata.get("file_name", "N/A"),
                "chunk_id": doc.metadata.get("chunk_id", "N/A"),
                "score": float(score)
            }
            retrieved_chunks.append(chunk_info)
            
        return retrieved_chunks

def retrieve_similar_chunks(query: str, k: int = 4) -> List[Dict[str, Any]]:
    """
    Convenience function: retrieve top-k relevant document chunks for a query.

    Instantiates an AirtelRetriever with the default vector store and delegates
    to its retrieve() method. Each returned chunk contains 'text', 'source_url',
    'file_name', 'chunk_id', and 'score' keys.
    """
    retriever = AirtelRetriever()
    return retriever.retrieve(query, k=k)

if __name__ == "__main__":
    sample_query = "How do I pitch Airtel Managed SD-WAN?"
    chunks = retrieve_similar_chunks(sample_query, k=4)
    print(f"Query: {sample_query}")
    print(f"Retrieved {len(chunks)} chunks:")
    for idx, c in enumerate(chunks, 1):
        print(f"\n--- Chunk {idx} (Score: {c['score']:.4f}) ---")
        print(f"Source: {c['source_url']}")
        print(f"Content:\n{c['text'][:200]}...")
