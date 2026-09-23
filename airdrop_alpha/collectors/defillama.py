"""
DefiLlama Protocols Collector for AirdropAlpha.
Fetches high-TVL tokenless protocols, chains, categories, and audit data.
"""

from typing import List, Dict, Any
from airdrop_alpha.collectors.base import BaseCollector, logger
from airdrop_alpha.core.models import CostTier

DEFILLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"


class DefiLlamaCollector(BaseCollector):
    def __init__(self, cache_ttl: int = 7200):
        # 2 hour cache for DefiLlama data
        super().__init__(name="defillama", cache_ttl=cache_ttl)

    def collect(self, use_cache: bool = True, min_tvl: float = 1_000_000.0) -> List[Dict[str, Any]]:
        """
        Collects tokenless protocols with TVL > min_tvl from DefiLlama.
        """
        if use_cache:
            cached = self.read_cache()
            if cached:
                return cached

        logger.info(f"[{self.name}] Fetching protocols from {DEFILLAMA_PROTOCOLS_URL}...")
        client = self.get_client()
        
        try:
            response = client.get(DEFILLAMA_PROTOCOLS_URL)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"[{self.name}] Network error: {e}")
            cached = self.read_cache()
            if cached:
                logger.info(f"[{self.name}] Falling back to stale cache.")
                return cached
            return []

        results = []
        for p in data:
            # Check if tokenless (no symbol or symbol is '-')
            symbol = p.get("symbol")
            if symbol and symbol != "-":
                continue
                
            tvl = p.get("tvl") or 0.0
            if tvl < min_tvl:
                continue
                
            name = p.get("name", "Unknown")
            slug = p.get("slug") or name.lower().replace(" ", "-")
            category = p.get("category", "DeFi")
            chains = p.get("chains", [])
            audit_links = p.get("audit_links") or []
            audits_count = p.get("audits", "0")
            
            # Form audit firms list
            audit_firms = []
            if isinstance(audit_links, list):
                for link in audit_links:
                    link_str = str(link).lower()
                    if "openzeppelin" in link_str:
                        audit_firms.append("OpenZeppelin")
                    elif "trailofbits" in link_str:
                        audit_firms.append("Trail of Bits")
                    elif "certik" in link_str:
                        audit_firms.append("CertiK")
                    elif "peckshield" in link_str:
                        audit_firms.append("PeckShield")
                    else:
                        audit_firms.append("Verified Auditor")
                        
            # Determine cost tier based on TVL and category
            # If TVL is significant, usually requires depositing/staking
            cost_tier = CostTier.CAPITAL_REQUIRED if tvl > 5_000_000 else CostTier.GAS_ONLY
            
            results.append({
                "id": f"llama-{p.get('id', slug)}",
                "name": name,
                "slug": slug,
                "source": "DefiLlama",
                "url": p.get("url", f"https://defillama.com/protocol/{slug}"),
                "website_url": p.get("url"),
                "twitter_handle": p.get("twitter"),
                "description": p.get("description", f"{name} is a high-TVL tokenless protocol in {category}."),
                "category": category,
                "chains": chains[:4] if chains else ["Multi-Chain"],
                "tvl_usd": float(tvl),
                "cost_tier": cost_tier.value,
                "is_free": False,
                "audit_firms": list(set(audit_firms)),
                "audits_count": int(audits_count) if str(audits_count).isdigit() else len(audit_firms),
            })
            
        logger.info(f"[{self.name}] Discovered {len(results)} high-potential tokenless protocols.")
        self.write_cache(results)
        return results
