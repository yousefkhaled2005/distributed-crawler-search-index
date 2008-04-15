"""
Bloom Filter URL Deduplication Engine
Copyright (c) 2008-2011 Yousef Khaled. All rights reserved.
"""

import math
import mmh3


class BloomFilter:
    """
    Space-efficient probabilistic data structure for web crawler URL deduplication.
    Guarantees zero false negatives and configurable false positive probability.
    """
    def __init__(self, expected_elements: int = 1000000, false_positive_rate: float = 0.01):
        self.expected_elements = expected_elements
        self.false_positive_rate = false_positive_rate
        
        # Optimal bit array size m = -(n * ln(p)) / (ln(2)^2)
        self.size = int(-1 * (expected_elements * math.log(false_positive_rate)) / (math.log(2) ** 2))
        
        # Optimal hash count k = (m / n) * ln(2)
        self.hash_count = int((self.size / expected_elements) * math.log(2))
        
        self.bit_array = bytearray(math.ceil(self.size / 8))
        self.count = 0

    def _get_hashes(self, item: str):
        h1 = mmh3.hash(item, 42)
        h2 = mmh3.hash(item, 84)
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size

    def add(self, item: str) -> None:
        for bit_index in self._get_hashes(item):
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            self.bit_array[byte_index] |= (1 << bit_offset)
        self.count += 1

    def contains(self, item: str) -> bool:
        for bit_index in self._get_hashes(item):
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            if not (self.bit_array[byte_index] & (1 << bit_offset)):
                return False
        return True

    def __contains__(self, item: str) -> bool:
        return self.contains(item)

    def current_false_positive_rate(self) -> float:
        return (1.0 - math.exp(-self.hash_count * self.count / self.size)) ** self.hash_count
