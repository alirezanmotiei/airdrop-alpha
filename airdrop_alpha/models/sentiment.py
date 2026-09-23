"""
NLP Social Sentiment & Community Scam Detection Engine for AirdropAlpha.
Parses discussions, comments, and threads from Reddit (r/CryptoAirdrop, r/airdrop, r/CryptoCurrency)
and Twitter/X to detect community scam alerts, wallet drainer warnings, and hype signals.
"""

import re
from typing import List, Dict, Tuple
from airdrop_alpha.core.models import SocialSentiment

# Community Red Flag / Scam Warning Lexicon
SCAM_WARNING_LEXICON = [
    "drainer", "wallet drainer", "phishing", "scam", "rug", "rugpull", "fake",
    "malicious", "stolen", "hack", "hacked", "honeypot", "lost my funds",
    "unlimited approval", "permit2 drain", "impersonator", "dont connect",
    "do not connect", "stealer", "scammer", "dust attack", "blacklist"
]

# Community Validation / Legitimacy Signals Lexicon
VALIDATION_LEXICON = [
    "legit", "confirmed airdrop", "binance labs", "paradigm", "a16z", "polychain",
    "dragonfly", "testnet faucet", "faucet works", "mainnet launched", "raised",
    "series a", "backed by", "audit passed", "great project", "easy tasks",
    "free airdrop", "early access", "tge soon", "points live", "claimable"
]


def analyze_text_sentiment(text: str) -> Tuple[int, int, List[str]]:
    """
    Scans a given body of text (post title, Reddit comment, tweet)
    for scam warning keywords and positive validation signals.
    
    Returns:
        (scam_warning_count, positive_signals_count, detected_warnings)
    """
    clean_text = text.lower()
    
    scam_count = 0
    positive_count = 0
    detected_warnings = []
    
    for phrase in SCAM_WARNING_LEXICON:
        matches = len(re.findall(r'\b' + re.escape(phrase) + r'\b', clean_text))
        if matches > 0:
            scam_count += matches
            detected_warnings.append(phrase)
            
    for phrase in VALIDATION_LEXICON:
        matches = len(re.findall(r'\b' + re.escape(phrase) + r'\b', clean_text))
        if matches > 0:
            positive_count += matches
            
    return scam_count, positive_count, detected_warnings


def evaluate_community_sentiment(
    texts: List[str],
    reddit_count: int = 0,
    twitter_count: int = 0,
) -> SocialSentiment:
    """
    Aggregates community sentiment across multiple posts/comments.
    Computes normalized sentiment score S_social in [-1.0, 1.0] and Hype Index (0 to 100).
    """
    total_scams = 0
    total_positives = 0
    all_warnings = set()
    sample_threads: List[Dict[str, str]] = []
    
    for item in texts:
        s_count, p_count, warns = analyze_text_sentiment(item)
        total_scams += s_count
        total_positives += p_count
        all_warnings.update(warns)
        
        if s_count > 0 or p_count > 0:
            sample_threads.append({
                "snippet": item[:160] + "..." if len(item) > 160 else item,
                "has_scam_warning": str(s_count > 0),
                "warnings": ", ".join(warns),
            })
            
    # Calculate Normalized Sentiment Score (-1.0 to +1.0)
    # Scam warnings are penalized 2.5x heavier than positive signals (asymmetrical risk)
    net_score = total_positives - (2.5 * total_scams)
    total_volume = total_positives + (2.5 * total_scams)
    
    if total_volume > 0:
        sentiment_score = round(max(-1.0, min(1.0, net_score / total_volume)), 2)
    else:
        sentiment_score = 0.0
        
    # Calculate Hype Index (0 to 100)
    # Combines mention velocity with positive sentiment
    total_mentions = reddit_count + twitter_count
    volume_factor = min(60.0, total_mentions * 2.0)
    sentiment_bonus = max(0.0, (sentiment_score + 1.0) * 20.0)  # 0 to 40 pts
    hype_index = round(min(100.0, max(10.0, volume_factor + sentiment_bonus)), 1)
    
    return SocialSentiment(
        reddit_mentions=reddit_count,
        twitter_mentions=twitter_count,
        sentiment_score=sentiment_score,
        scam_warning_count=total_scams,
        positive_signals=total_positives,
        hype_index=hype_index,
        sample_threads=sample_threads[:5],
    )
