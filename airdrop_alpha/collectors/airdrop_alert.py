"""
Live AirdropAlert RSS Feed Collector for AirdropAlpha.
Parses verified airdrop listings, full task instructions, whitepaper/website links,
and accurately classifies cost requirements (100% Free vs Gas vs Capital).
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from datetime import datetime

from airdrop_alpha.collectors.base import BaseCollector, logger
from airdrop_alpha.core.models import (
    CostTier, TaskType, TaskRequirement, FundingData, VCTier
)

RSS_FEED_URL = "https://airdropalert.com/feed/rssfeed"


class AirdropAlertCollector(BaseCollector):
    def __init__(self, cache_ttl: int = 3600):
        super().__init__(name="airdrop_alert", cache_ttl=cache_ttl)

    def _determine_cost_tier(self, title: str, description: str, content: str) -> CostTier:
        """
        Infers whether the airdrop is 100% Free, Gas-Only, or Capital Required based on text semantics.
        """
        combined = f"{title} {description} {content}".lower()
        
        # Capital-required indicators
        if any(w in combined for w in ["deposit", "stake", "staking", "lockup", "liquidity provider", "hold at least", "buy and hold"]):
            return CostTier.CAPITAL_REQUIRED
            
        # Gas-only indicators
        if any(w in combined for w in ["mainnet tx", "bridge funds", "swap on", "mint nft on mainnet", "gas fee required"]):
            return CostTier.GAS_ONLY
            
        # Default for testnets, faucets, quests, social tasks
        return CostTier.FREE_TASKS_ONLY

    def _extract_guide_steps(self, content_html: str) -> List[str]:
        """Extracts bullet points / numbered guide steps from HTML content."""
        steps = []
        # Match <li>...</li> or numbered lines
        raw_items = re.findall(r'<li[^>]*>(.*?)</li>', content_html, re.DOTALL | re.IGNORECASE)
        for item in raw_items:
            clean = re.sub(r'<[^>]+>', '', item).strip()
            if clean and len(clean) > 8:
                steps.append(clean)
                
        if not steps:
            # Fallback to paragraph splitting
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content_html, re.DOTALL | re.IGNORECASE)
            for p in paragraphs:
                clean = re.sub(r'<[^>]+>', '', p).strip()
                if clean and any(k in clean.lower() for k in ["step", "visit", "connect", "follow", "complete", "claim"]):
                    steps.append(clean)
                    
        return steps[:8]

    def _extract_category_and_chain(self, text: str) -> tuple[str, List[str]]:
        """Infers the category (DeFi, L1/L2, AI, DePIN) and blockchains."""
        clean = text.lower()
        
        # Category heuristics
        category = "DeFi"
        if any(w in clean for w in ["layer 1", "layer 2", "l2", "rollup", "evm chain"]):
            category = "L1/L2"
        elif any(w in clean for w in ["ai", "artificial intelligence", "agent", "gpu", "machine learning"]):
            category = "AI / Crypto"
        elif any(w in clean for w in ["depin", "hardware", "bandwidth", "node"]):
            category = "DePIN"
        elif any(w in clean for w in ["game", "gaming", "play-to-earn", "metaverse"]):
            category = "GameFi"
        elif any(w in clean for w in ["social", "telegram", "bot", "tap-to-earn"]):
            category = "SocialFi"
            
        # Chain heuristics
        chains = []
        for ch in ["ethereum", "solana", "arbitrum", "base", "polygon", "optimism", "sui", "aptos", "ton", "bsc", "avalanche"]:
            if ch in clean:
                chains.append(ch.capitalize())
        if not chains:
            chains = ["EVM Compatible"]
            
        return category, chains

    def collect(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Collects active airdrops from AirdropAlert RSS feed.
        """
        if use_cache:
            cached = self.read_cache()
            if cached:
                return cached

        logger.info(f"[{self.name}] Fetching live feed from {RSS_FEED_URL}...")
        client = self.get_client()
        
        try:
            response = client.get(RSS_FEED_URL)
            response.raise_for_status()
            xml_text = response.text
        except Exception as e:
            logger.error(f"[{self.name}] Network error: {e}")
            cached = self.read_cache()
            if cached:
                logger.info(f"[{self.name}] Falling back to stale cache.")
                return cached
            return []

        # Parse XML
        items_data = []
        try:
            root = ET.fromstring(xml_text)
            items = root.findall(".//item")
            
            for idx, item in enumerate(items):
                title = item.find("title").text if item.find("title") is not None else f"Airdrop-{idx}"
                link = item.find("link").text if item.find("link") is not None else ""
                desc = item.find("description").text if item.find("description") is not None else ""
                
                # Content encoded
                content_elem = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
                content = content_elem.text if content_elem is not None else desc
                
                website_link = item.find("website_link").text if item.find("website_link") is not None else None
                whitepaper_link = item.find("white_paper_link").text if item.find("white_paper_link") is not None else None
                
                # Clean clean description text
                clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
                cost_tier = self._determine_cost_tier(title, clean_desc, content)
                category, chains = self._extract_category_and_chain(f"{title} {clean_desc}")
                guide_steps = self._extract_guide_steps(content)
                
                slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
                
                # Check for notable VC mentions in description
                combined_text = f"{title} {clean_desc} {content}".lower()
                vc_tier = VCTier.UNBACKED
                lead_investors = []
                for vc, tier in [
                    ("paradigm", VCTier.TIER_1), ("a16z", VCTier.TIER_1),
                    ("binance labs", VCTier.TIER_1), ("polychain", VCTier.TIER_1),
                    ("dragonfly", VCTier.TIER_1), ("coinbase ventures", VCTier.TIER_2),
                    ("multicoin", VCTier.TIER_2), ("pantera", VCTier.TIER_2),
                ]:
                    if vc in combined_text:
                        vc_tier = tier
                        lead_investors.append(vc.title())
                        
                items_data.append({
                    "id": f"aa-{slug}",
                    "name": title,
                    "slug": slug,
                    "source": "AirdropAlert",
                    "url": link,
                    "website_url": website_link,
                    "whitepaper_url": whitepaper_link,
                    "description": clean_desc[:400] if clean_desc else title,
                    "category": category,
                    "chains": chains,
                    "cost_tier": cost_tier.value,
                    "is_free": cost_tier == CostTier.FREE_TASKS_ONLY,
                    "guide_steps": guide_steps,
                    "vc_tier": vc_tier.value,
                    "lead_investors": lead_investors,
                    "raw_content": content[:1200],
                })
                
            logger.info(f"[{self.name}] Successfully parsed {len(items_data)} airdrops from feed.")
            self.write_cache(items_data)
            return items_data
            
        except Exception as e:
            logger.error(f"[{self.name}] Failed to parse XML: {e}")
            return []
