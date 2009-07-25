"""
Distributed Inverted Index and Okapi BM25 Scoring Engine
Copyright (c) 2008-2011 Yousef Khaled.
"""

import math
import re
from collections import defaultdict
from typing import Dict, List, Tuple
from .compression import VByteCodec


class InvertedIndex:
    """
    Memory-mapped Inverted Index supporting compressed postings, document lengths,
    and Okapi BM25 statistical relevance scoring.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.index: Dict[str, bytes] = {} # term -> compressed postings bytes
        self.term_freqs: Dict[str, Dict[int, int]] = defaultdict(dict) # term -> {doc_id: count}
        self.doc_lengths: Dict[int, int] = {}
        self.doc_store: Dict[int, Dict] = {}
        self.avg_doc_length: float = 0.0
        self.total_docs: int = 0

    def tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_؀-ۿ]{2,}\b", text)]

    def add_document(self, doc_id: int, title: str, text: str, url: str) -> None:
        tokens = self.tokenize(title + " " + text)
        doc_len = len(tokens)
        self.doc_lengths[doc_id] = doc_len
        self.doc_store[doc_id] = {"title": title, "url": url, "text": text[:300]}
        
        freqs = defaultdict(int)
        for t in tokens:
            freqs[t] += 1
            
        for term, cnt in freqs.items():
            self.term_freqs[term][doc_id] = cnt
            
        self.total_docs += 1
        self.avg_doc_length = sum(self.doc_lengths.values()) / self.total_docs

    def build_compressed_index(self) -> None:
        for term, doc_dict in self.term_freqs.items():
            doc_ids = sorted(list(doc_dict.keys()))
            self.index[term] = VByteCodec.encode_postings(doc_ids)

    def search_bm25(self, query: str, top_k: int = 10) -> List[Tuple[int, float, Dict]]:
        query_terms = self.tokenize(query)
        scores = defaultdict(float)

        for term in query_terms:
            if term not in self.index:
                continue
            
            # Decompress postings list
            doc_ids = VByteCodec.decode_postings(self.index[term])
            df = len(doc_ids)
            # Standard Lucene/BM25 IDF with smoothing
            idf = math.log(1.0 + (self.total_docs - df + 0.5) / (df + 0.5))

            for doc_id in doc_ids:
                tf = self.term_freqs[term].get(doc_id, 0)
                dl = self.doc_lengths.get(doc_id, self.avg_doc_length)
                
                # Okapi BM25 TF formula
                tf_norm = (tf * (self.k1 + 1.0)) / (tf + self.k1 * (1.0 - self.b + self.b * (dl / self.avg_doc_length)))
                scores[doc_id] += idf * tf_norm

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(doc_id, score, self.doc_store[doc_id]) for doc_id, score in ranked]
