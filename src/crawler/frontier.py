"""
Distributed URL Frontier and Host Politeness Scheduler
Copyright (c) 2008-2011 Yousef Khaled.
"""

import time
import urllib.parse
from collections import defaultdict, deque
from typing import Optional, Dict


class URLFrontier:
    """
    Host-aware URL Frontier ensuring crawl politeness (RFC 9309).
    Enforces minimum delay per domain to prevent overwhelming target hosts.
    """
    def __init__(self, default_crawl_delay_sec: float = 0.5):
        self.default_crawl_delay = default_crawl_delay_sec
        self.host_queues: Dict[str, deque] = defaultdict(deque)
        self.host_last_access: Dict[str, float] = defaultdict(float)
        self.total_enqueued = 0

    def extract_host(self, url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.lower()

    def enqueue(self, url: str) -> None:
        host = self.extract_host(url)
        self.host_queues[host].append(url)
        self.total_enqueued += 1

    def dequeue(self) -> Optional[str]:
        now = time.time()
        for host, queue in self.host_queues.items():
            if queue:
                last_time = self.host_last_access[host]
                if now - last_time >= self.default_crawl_delay:
                    self.host_last_access[host] = now
                    return queue.popleft()
        return None

    def size(self) -> int:
        return sum(len(q) for q in self.host_queues.values())
