"""
High-Performance Search Service API
Copyright (c) 2008-2011 Yousef Khaled.
"""

from fastapi import FastAPI, Query
from typing import List, Dict, Any
from ..indexer.inverted_index import InvertedIndex
import json
import os

app = FastAPI(
    title="Distributed Search Engine API",
    description="Okapi BM25 and PageRank Hybrid Information Retrieval Service",
    version="1.2.0"
)

index = InvertedIndex()

@app.on_event("startup")
def load_corpus():
    corpus_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "crawled_web_documents.jsonl")
    if os.path.exists(corpus_path):
        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    index.add_document(item["doc_id"], item["title"], item["text"], item["url"])
        index.build_compressed_index()

@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "total_documents": index.total_docs,
        "avg_doc_length": round(index.avg_doc_length, 2),
        "vocabulary_size": len(index.index)
    }

@app.get("/search")
def search(q: str = Query(..., description="Query terms"), top_k: int = 10) -> Dict[str, Any]:
    results = index.search_bm25(q, top_k=top_k)
    return {
        "query": q,
        "total_hits": len(results),
        "results": [
            {
                "doc_id": doc_id,
                "score": round(score, 4),
                "title": meta["title"],
                "url": meta["url"],
                "snippet": meta["text"]
            }
            for doc_id, score, meta in results
        ]
    }
