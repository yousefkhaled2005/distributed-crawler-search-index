"""
Comprehensive Unit Test Suite for Crawler & Search Index
Copyright (c) 2008-2011 Yousef Khaled.
"""

import pytest
from src.indexer.bloom_filter import BloomFilter
from src.indexer.compression import VByteCodec
from src.indexer.inverted_index import InvertedIndex
from src.ranking.pagerank import PageRankEngine
from src.crawler.frontier import URLFrontier


def test_bloom_filter_dedup():
    bf = BloomFilter(expected_elements=1000, false_positive_rate=0.01)
    urls = [f"https://example.com/page_{i}" for i in range(200)]
    for u in urls:
        bf.add(u)
    for u in urls:
        assert u in bf
    assert "https://example.com/unseen_random_page_9999" not in bf


def test_vbyte_compression():
    doc_ids = [12, 18, 45, 128, 255, 1024, 65536]
    encoded = VByteCodec.encode_postings(doc_ids)
    decoded = VByteCodec.decode_postings(encoded)
    assert decoded == doc_ids


def test_inverted_index_bm25():
    idx = InvertedIndex()
    idx.add_document(1, "Distributed Consensus", "Raft and Paxos solve consensus in distributed systems.", "http://a.com")
    idx.add_document(2, "Web Search Indexing", "Inverted indexes allow fast full text search.", "http://b.com")
    idx.add_document(3, "Distributed Systems", "Consensus algorithms ensure database cluster reliability.", "http://c.com")
    idx.build_compressed_index()

    res = idx.search_bm25("Distributed Consensus", top_k=2)
    assert len(res) >= 2
    top_doc_id = res[0][0]
    assert top_doc_id in (1, 3)


def test_pagerank_convergence():
    pr = PageRankEngine()
    pr.add_edge("A", "B")
    pr.add_edge("B", "C")
    pr.add_edge("C", "A")
    ranks = pr.compute()
    assert len(ranks) == 3
    # In a symmetric circular graph, PageRanks should be identical
    assert pytest.approx(ranks["A"], 0.001) == ranks["B"]
    assert pytest.approx(ranks["B"], 0.001) == ranks["C"]
