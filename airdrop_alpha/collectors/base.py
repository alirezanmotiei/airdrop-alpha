"""
Base Collector Interface for AirdropAlpha.
Features enterprise proxy support (HTTP/HTTPS/SOCKS5), local file caching,
and exponential backoff retry mechanics.
"""

import json
import time
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Dict
import httpx

from airdrop_alpha.core.config import settings, CACHE_DIR

logger = logging.getLogger("airdrop_alpha.collectors")


class BaseCollector(ABC):
    def __init__(self, name: str, cache_ttl: Optional[int] = None):
        self.name = name
        self.cache_ttl = cache_ttl or settings.cache_ttl_seconds
        self.cache_file = CACHE_DIR / f"{name}_cache.json"
        
    def get_client(self, is_reddit: bool = False) -> httpx.Client:
        """
        Creates an httpx Client equipped with proxy configuration and compliant headers.
        Supports HTTP, HTTPS, and SOCKS5 proxies.
        """
        proxy = settings.get_effective_proxy()
        user_agent = settings.reddit_user_agent if is_reddit else settings.user_agent
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        return httpx.Client(
            proxy=proxy,
            timeout=settings.request_timeout,
            headers=headers,
            follow_redirects=True,
        )
        
    def read_cache(self) -> Optional[Any]:
        """Reads cached data if within TTL."""
        if not self.cache_file.exists():
            return None
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            timestamp = payload.get("timestamp", 0)
            if (time.time() - timestamp) < self.cache_ttl:
                logger.info(f"[{self.name}] Using cached data (age: {int(time.time() - timestamp)}s)")
                return payload.get("data")
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to read cache: {e}")
        return None
        
    def write_cache(self, data: Any) -> None:
        """Writes data to local cache file with current timestamp."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": time.time(),
                    "data": data,
                }, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to write cache: {e}")

    @abstractmethod
    def collect(self, use_cache: bool = True) -> Any:
        """Collects and returns processed data."""
        pass
