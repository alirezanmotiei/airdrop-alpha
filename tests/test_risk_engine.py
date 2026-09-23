import pytest
from airdrop_alpha.core.models import FundingData, VCTier, SocialSentiment, RiskLevel
from airdrop_alpha.models.risk_engine import evaluate_risk_profile


def test_risk_profile_tier_1_audit_and_vc():
    funding = FundingData(
        vc_tier=VCTier.TIER_1,
        lead_investors=["Paradigm", "Binance Labs"],
    )
    social = SocialSentiment(sentiment_score=0.5, scam_warning_count=0)
    audits = ["OpenZeppelin", "Trail of Bits"]
    
    profile = evaluate_risk_profile(
        name="Tier1Protocol",
        description="Top L2 protocol",
        funding=funding,
        social=social,
        audit_mentions=audits,
    )
    assert profile.safety_score >= 70.0
    assert profile.risk_level == RiskLevel.LOW
    assert profile.drainer_risk is False


def test_risk_profile_drainer_alert():
    funding = FundingData(vc_tier=VCTier.UNBACKED)
    social = SocialSentiment(scam_warning_count=5, sentiment_score=-0.8)
    
    profile = evaluate_risk_profile(
        name="SuspiciousDrop",
        description="Claim 10000 FREE tokens now!",
        funding=funding,
        social=social,
        audit_mentions=[],
    )
    assert profile.drainer_risk is True
    assert profile.risk_level == RiskLevel.CRITICAL_SCAM
    assert profile.safety_score < 40.0
