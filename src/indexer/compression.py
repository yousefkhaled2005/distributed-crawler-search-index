"""
Variable Byte (VByte) Integer Compression for Inverted Index Posting Lists
Copyright (c) 2008-2011 Yousef Khaled.
"""

from typing import List


class VByteCodec:
    """
    Encodes and decodes docID postings lists using Variable Byte (VByte) compression.
    High-density gap-encoding reduces inverted index storage by 75-85%.
    """
    @staticmethod
    def encode_number(number: int) -> bytes:
        bytes_list = []
        while True:
            bytes_list.insert(0, number % 128)
            if number < 128:
                break
            number //= 128
        bytes_list[-1] += 128 # Set high-order continuation bit on the terminal byte
        return bytes(bytes_list)

    @classmethod
    def encode_postings(cls, doc_ids: List[int]) -> bytes:
        if not doc_ids:
            return b""
        encoded = bytearray()
        prev = 0
        for doc_id in sorted(doc_ids):
            gap = doc_id - prev
            encoded.extend(cls.encode_number(gap))
            prev = doc_id
        return bytes(encoded)

    @staticmethod
    def decode_postings(encoded: bytes) -> List[int]:
        doc_ids = []
        n = 0
        current_doc = 0
        for byte in encoded:
            if byte < 128:
                n = 128 * n + byte
            else:
                n = 128 * n + (byte - 128)
                current_doc += n
                doc_ids.append(current_doc)
                n = 0
        return doc_ids
