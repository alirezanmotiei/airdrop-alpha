import pytest
from airdrop_alpha.models.sentiment import (
    analyze_text_sentiment, evaluate_community_sentiment
)


def test_analyze_text_sentiment_scam_detection():
    sample_scam = "Beware this site is a wallet drainer! It stole my tokens after unlimited approval."
    scam_count, pos_count, warnings = analyze_text_sentiment(sample_scam)
    assert scam_count >= 2
    assert "drainer" in warnings or "wallet drainer" in warnings


def test_analyze_text_sentiment_positive_validation():
    sample_pos = "Airdrop confirmed! Backed by Binance Labs and Paradigm, easy testnet faucet tasks."
    scam_count, pos_count, warnings = analyze_text_sentiment(sample_pos)
    assert pos_count >= 2
    assert scam_count == 0


def test_evaluate_community_sentiment_aggregation():
    texts = [
        "Great project, airdrop confirmed and easy testnet faucet!",
        "Legit team, backed by Paradigm and tier 1 VCs",
        "Wait, someone in telegram said wallet drainer alert!",
    ]
    sentiment = evaluate_community_sentiment(texts, reddit_count=3, twitter_count=5)
    assert sentiment.scam_warning_count >= 1
    assert sentiment.positive_signals >= 2
    assert -1.0 <= sentiment.sentiment_score <= 1.0
    assert 0 <= sentiment.hype_index <= 100
