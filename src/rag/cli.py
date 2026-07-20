"""
CLI Interface for Airtel B2B RAG Retriever
Allows querying vector store from terminal and displaying top-k retrieved chunks with source citations.
"""

import sys
import argparse
from src.rag.retriever import retrieve_similar_chunks

def main():
    parser = argparse.ArgumentParser(description="Airtel B2B AI Sales Assistant - RAG Retriever CLI")
    parser.add_argument("query", type=str, nargs="?", help="Question or query about Airtel B2B products")
    parser.add_argument("-q", "--query-option", type=str, help="Alternative query flag")
    parser.add_argument("-k", "--top-k", type=int, default=4, help="Number of top chunks to retrieve (default: 4)")
    
    args = parser.parse_args()
    query_text = args.query or args.query_option
    
    if not query_text:
        query_text = input("Enter your Airtel B2B product question: ").strip()
        if not query_text:
            print("Error: No query provided.")
            sys.exit(1)
            
    print(f"\n=======================================================")
    print(f" Query: {query_text}")
    print(f" Top-K Chunks Requested: {args.top_k}")
    print(f"=======================================================\n")
    
    results = retrieve_similar_chunks(query_text, k=args.top_k)
    
    if not results:
        print("No relevant chunks found.")
        return
        
    for i, res in enumerate(results, 1):
        print(f"[{i}] Relevance Score: {res['score']:.4f}")
        print(f"    Source URL: {res['source_url']}")
        print(f"    File Name:  {res['file_name']}")
        print(f"    Chunk ID:   {res['chunk_id']}")
        print(f"    Snippet:\n")
        indented_text = "\n".join("      " + line for line in res['text'].split("\n"))
        print(indented_text)
        print("-" * 60)

if __name__ == "__main__":
    main()
