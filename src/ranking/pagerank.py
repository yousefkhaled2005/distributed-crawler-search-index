"""
PageRank Eigenvector Power Iteration Engine
Copyright (c) 2008-2011 Yousef Khaled.
"""

from collections import defaultdict
from typing import Dict, List, Set


class PageRankEngine:
    """
    Computes web graph authority distribution using PageRank power iteration.
    Handles dangling nodes and teleports with damping factor alpha = 0.85.
    """
    def __init__(self, damping_factor: float = 0.85, max_iter: int = 100, tolerance: float = 1e-6):
        self.alpha = damping_factor
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.adj_list: Dict[str, Set[str]] = defaultdict(set)
        self.nodes: Set[str] = set()

    def add_edge(self, src: str, dest: str) -> None:
        self.nodes.add(src)
        self.nodes.add(dest)
        self.adj_list[src].add(dest)

    def compute(self) -> Dict[str, float]:
        N = len(self.nodes)
        if N == 0:
            return {}

        node_list = sorted(list(self.nodes))
        ranks = {node: 1.0 / N for node in node_list}

        for iteration in range(self.max_iter):
            new_ranks = defaultdict(float)
            dangling_sum = 0.0

            for node in node_list:
                out_degree = len(self.adj_list[node])
                if out_degree == 0:
                    dangling_sum += ranks[node]
                else:
                    share = ranks[node] / out_degree
                    for target in self.adj_list[node]:
                        new_ranks[target] += share

            # Add random teleport probability and distributed dangling mass
            base_prob = (1.0 - self.alpha) / N + (self.alpha * dangling_sum) / N
            diff = 0.0
            for node in node_list:
                updated = base_prob + self.alpha * new_ranks[node]
                diff += abs(updated - ranks[node])
                ranks[node] = updated

            if diff < self.tolerance:
                break

        return ranks
