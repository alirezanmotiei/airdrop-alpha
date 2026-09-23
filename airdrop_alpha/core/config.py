"""
Configuration and Environment Settings for AirdropAlpha.
Supports enterprise proxies (HTTP/HTTPS/SOCKS5), API rate limiting, and cache control.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"

DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)


class Settings(BaseModel):
    # Networking & Proxy Configuration
    # Supports HTTP, HTTPS, and SOCKS5 proxies (e.g. socks5://127.0.0.1:10808 or http://127.0.0.1:7890)
    http_proxy: Optional[str] = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy: Optional[str] = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    all_proxy: Optional[str] = os.getenv("ALL_PROXY") or os.getenv("all_proxy")
    
    # Request Headers
    user_agent: str = os.getenv(
        "AIRDROP_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AirdropAlpha/1.0.0 (Research Bot)"
    )
    reddit_user_agent: str = os.getenv(
        "REDDIT_USER_AGENT",
        "python:airdropalpha:v1.0.0 (by /u/airdrop_researcher)"
    )
    
    # Cache and Timeout settings
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "15.0"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default
    
    # Financial Modeling Defaults
    benchmark_hourly_wage: float = 25.0       # $25/hour standard reference wage
    risk_free_rate_apy: float = 0.05          # 5% annual risk-free rate for capital cost
    default_airdrop_share: float = 0.08       # 8% typical community token pool allocation
    default_sybil_filter_rate: float = 0.50   # 50% average sybil disqualification rate
    
    def get_effective_proxy(self) -> Optional[str]:
        """Returns the most appropriate proxy configured in environment."""
        return self.all_proxy or self.https_proxy or self.http_proxy


settings = Settings()
