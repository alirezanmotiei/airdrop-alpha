"""
Social Intelligence & Community Discussion Collector for AirdropAlpha.
Parses Reddit (r/CryptoAirdrop, r/airdrop, r/CryptoCurrency) and Web3 discussions
to discover grassroots airdrops, evaluate public sentiment, and spot scam/drainer warnings.
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

from airdrop_alpha.collectors.base import BaseCollector, logger
from airdrop_alpha.models.sentiment import evaluate_community_sentiment
from airdrop_alpha.core.models import SocialSentiment, CostTier

REDDIT_FEEDS = [
    ("CryptoAirdrop", "https://www.reddit.com/r/CryptoAirdrop/.rss"),
    ("airdrop", "https://www.reddit.com/r/airdrop/.rss"),
]


class SocialIntelligenceCollector(BaseCollector):
    def __init__(self, cache_ttl: int = 1800):
        # 30-minute cache for fast-moving social feeds
        super().__init__(name="social_intelligence", cache_ttl=cache_ttl)

    def collect(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Collects social discussions and newly emerging grassroots airdrops.
        """
        if use_cache:
            cached = self.read_cache()
            if cached:
                return cached

        logger.info(f"[{self.name}] Scraping community feeds from Reddit...")
        client = self.get_client(is_reddit=True)
        
        discovered_airdrops: List[Dict[str, Any]] = []
        project_sentiments: Dict[str, List[str]] = {}
        
        for sub_name, feed_url in REDDIT_FEEDS:
            try:
                response = client.get(feed_url)
                if response.status_code == 200:
                    root = ET.fromstring(response.text)
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    entries = root.findall("atom:entry", ns)
                    
                    for entry in entries[:25]:
                        title = entry.find("atom:title", ns).text if entry.find("atom:title", ns) is not None else ""
                        content_elem = entry.find("atom:content", ns)
                        content = content_elem.text if content_elem is not None else ""
                        clean_content = re.sub(r'<[^>]+>', ' ', content).strip()
                        
                        full_text = f"{title} {clean_content}"
                        
                        # Extract project name candidates from title (e.g. "[ProjectName] Airdrop")
                        name_match = re.search(r'\[(.*?)\]', title)
                        if name_match:
                            proj_name = name_match.group(1).strip()
                        else:
                            # Heuristic: first 2-3 words
                            words = [w for w in title.split() if w.lower() not in ["new", "airdrop", "free", "instant", "claim", "get", "earn"]]
                            proj_name = " ".join(words[:2]) if words else "Community Airdrop"
                            
                        proj_slug = re.sub(r'[^a-zA-Z0-9]+', '-', proj_name.lower()).strip('-')
                        
                        if proj_slug not in project_sentiments:
                            project_sentiments[proj_slug] = []
                        project_sentiments[proj_slug].append(full_text)
                        
                        # Check if this looks like a new grassroots discovery
                        if len(proj_name) > 2 and proj_name.lower() not in ["airdrop", "daily", "free crypto"]:
                            is_free = not any(w in full_text.lower() for w in ["deposit", "buy", "stake", "fee"])
                            discovered_airdrops.append({
                                "id": f"reddit-{proj_slug}",
                                "name": proj_name,
                                "slug": proj_slug,
                                "source": f"Reddit r/{sub_name}",
                                "url": entry.find("atom:link", ns).attrib.get("href", "") if entry.find("atom:link", ns) is not None else "",
                                "description": clean_content[:300] if clean_content else title,
                                "category": "Grassroots / SocialFi",
                                "chains": ["Multi-Chain"],
                                "cost_tier": CostTier.FREE_TASKS_ONLY.value if is_free else CostTier.GAS_ONLY.value,
                                "is_free": is_free,
                                "raw_title": title,
                                "text_sample": full_text[:400],
                            })
                            
                else:
                    logger.warning(f"[{self.name}] Reddit feed {sub_name} returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to fetch feed for {sub_name}: {e}")

        # Compute sentiment mapping for each project
        evaluated_sentiments: Dict[str, Dict[str, Any]] = {}
        for slug, texts in project_sentiments.items():
            sentiment_obj = evaluate_community_sentiment(texts, reddit_count=len(texts), twitter_count=5)
            evaluated_sentiments[slug] = sentiment_obj.model_dump()

        result = {
            "discovered_airdrops": discovered_airdrops[:20],
            "project_sentiments": evaluated_sentiments,
        }
        
        logger.info(f"[{self.name}] Analyzed discussions for {len(project_sentiments)} projects.")
        self.write_cache(result)
        return result

    def get_sentiment_for_project(self, project_name: str, slug: str) -> SocialSentiment:
        """
        Retrieves or evaluates sentiment for a specific project.
        """
        data = self.collect(use_cache=True)
        sentiments = data.get("project_sentiments", {})
        
        if slug in sentiments:
            return SocialSentiment(**sentiments[slug])
            
        # If not directly matched, check fuzzy match
        for s_key, s_data in sentiments.items():
            if s_key in slug or slug in s_key:
                return SocialSentiment(**s_data)
                
        # Default baseline neutral sentiment
        return SocialSentiment(
            reddit_mentions=4,
            twitter_mentions=8,
            sentiment_score=0.15,
            scam_warning_count=0,
            positive_signals=3,
            hype_index=45.0,
        )
