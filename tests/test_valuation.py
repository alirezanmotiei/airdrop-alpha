import pytest
from airdrop_alpha.core.models import FundingData, VCTier
from airdrop_alpha.models.valuation import (
    estimate_implied_fdv, calculate_airdrop_pool_value, SECTOR_MULTIPLIERS
)


def test_estimate_implied_fdv_tvl_based():
    funding = FundingData()
    fdv = estimate_implied_fdv(
        category="L1/L2",
        tvl_usd=100_000_000.0,
        funding=funding,
    )
    # L1/L2 sector multiplier is 5.5
    # 70% of 100M * 5.5 + 30% baseline
    assert fdv > 200_000_000.0


def test_estimate_implied_fdv_vc_step_up():
    funding = FundingData(
        total_raised_usd=20_000_000.0,
        last_round_valuation_usd=100_000_000.0,
        vc_tier=VCTier.TIER_1,
    )
    fdv = estimate_implied_fdv(
        category="DeFi",
        tvl_usd=0.0,
        funding=funding,
    )
    # 100M * 1.6 step up = 160M
    assert fdv >= 100_000_000.0


def test_calculate_airdrop_pool_value():
    pool = calculate_airdrop_pool_value(implied_fdv=100_000_000.0, community_allocation_pct=0.10)
    assert pool == 10_000_000.0
