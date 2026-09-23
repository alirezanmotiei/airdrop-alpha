import pytest
from airdrop_alpha.core.models import (
    AirdropProject, CostTier, FinancialMetrics, RiskProfile, FundingData, SocialSentiment
)
from airdrop_alpha.reporting.memo import generate_investment_memo


@pytest.fixture
def sample_memo_project():
    return AirdropProject(
        id="sample-1",
        name="Test Airdrop",
        slug="test-airdrop",
        cost_tier=CostTier.FREE_TASKS_ONLY,
        is_free=True,
        category="DeFi",
        chains=["Ethereum", "Arbitrum"],
        description="A groundbreaking Web3 protocol rewarding early contributors.",
        guide_steps=["Step 1: Connect wallet", "Step 2: Complete quest"],
        metrics=FinancialMetrics(
            implied_fdv=50_000_000.0,
            airdrop_pool_usd=5_000_000.0,
            expected_reward_usd=250.0,
            net_profit_usd=250.0,
            hourly_wage_usd=125.0,
            hours_per_10usd=0.08,
            alpha_score=88.0,
        ),
        funding=FundingData(
            total_raised_usd=10_000_000.0,
            lead_investors=["Paradigm"],
        ),
        social=SocialSentiment(
            sentiment_score=0.6,
            scam_warning_count=0,
            hype_index=75.0,
        ),
        risk=RiskProfile(
            safety_score=82.0,
        ),
    )


def test_generate_investment_memo_english(sample_memo_project):
    memo_en = generate_investment_memo(sample_memo_project, lang="en")
    assert "INSTITUTIONAL AIRDROP MEMORANDUM" in memo_en
    assert "100% FREE - ZERO INITIAL CAPITAL" in memo_en
    assert "$125.00 / hr" in memo_en
    assert "0.08 Hours" in memo_en


def test_generate_investment_memo_persian(sample_memo_project):
    memo_fa = generate_investment_memo(sample_memo_project, lang="fa")
    assert "یادداشت تحلیلی سرمایه‌گذاری ایردراپ" in memo_fa
    assert "۱۰۰٪ رایگان - بدون نیاز به سرمایه اولیه" in memo_fa
    assert "مدل کمی‌سازی ارزش و بازده اقتصادی" in memo_fa
    assert "چک‌لیست جلوگیری از شناسایی به عنوان سیبیل" in memo_fa
    assert 'dir="rtl"' in memo_fa
