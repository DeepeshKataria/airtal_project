"""
Airtel B2B Data Ingestion and Chunking Pipeline
Reads raw pages from data/raw/, dedupes, chunks text with metadata, and outputs to data/processed/chunks.json.
"""

import os
import re
import json
import hashlib
from typing import List, Dict, Any

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed")
OUTPUT_CHUNKS_FILE = os.path.join(PROCESSED_DATA_DIR, "chunks.json")

# Chunk size 800 chars (~150-200 words) with 100 char overlap preserves full paragraphs and product feature specs for RAG retrieval without fragmenting context.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

def extract_source_url(content: str) -> tuple[str, str]:
    match = re.search(r'<!--\s*Source URL:\s*(.*?)\s*-->', content)
    url = match.group(1) if match else "Unknown Source"
    cleaned_content = re.sub(r'<!--\s*Source URL:\s*.*?\s*-->', '', content).strip()
    return url, cleaned_content

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []
    
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{para}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(para) > chunk_size:
                # Sub-split long paragraph by sentences or fixed character step
                sub_start = 0
                while sub_start < len(para):
                    sub_end = sub_start + chunk_size
                    chunks.append(para[sub_start:sub_end])
                    sub_start += (chunk_size - overlap)
                current_chunk = ""
            else:
                current_chunk = para
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def process_raw_documents() -> List[Dict[str, Any]]:
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        return []
        
    raw_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(('.md', '.txt'))]
    all_chunks = []
    seen_chunk_hashes = set()
    
    for file_name in sorted(raw_files):
        file_path = os.path.join(RAW_DATA_DIR, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        url, cleaned_text = extract_source_url(content)
        raw_chunks = chunk_text(cleaned_text)
        
        for idx, chunk_str in enumerate(raw_chunks):
            # Deduplicate exact chunk text across documents
            chunk_hash = hashlib.md5(chunk_str.strip().encode('utf-8')).hexdigest()
            if chunk_hash in seen_chunk_hashes:
                continue
            seen_chunk_hashes.add(chunk_hash)
            
            chunk_obj = {
                "id": f"{file_name}_chunk_{idx}",
                "text": chunk_str.strip(),
                "source_url": url,
                "file_name": file_name,
                "chunk_index": idx
            }
            all_chunks.append(chunk_obj)
            
    with open(OUTPUT_CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
    return all_chunks

if __name__ == "__main__":
    chunks = process_raw_documents()
    print(f"Processed {len(chunks)} unique chunks saved to {OUTPUT_CHUNKS_FILE}")
