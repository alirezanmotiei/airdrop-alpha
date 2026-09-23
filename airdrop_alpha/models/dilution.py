"""
Dilution and Cohort Distribution Engine for AirdropAlpha.
Calculates Sybil discounts and tiered Pareto distributions to estimate realistic user rewards.
"""

from typing import Dict, Tuple

# Pareto Cohort Distributions derived from empirical airdrop data (Arbitrum, Starknet, Wormhole, LayerZero)
# Tier 1 (Whales / Core Protocol Contributors - Top 5%): 35% of total pool
# Tier 2 (Power Users / Consistent Farmers - Next 25%): 45% of total pool
# Tier 3 (Casual / Free Task Hunters - Remaining 70%): 20% of total pool
TIER_WEIGHTS: Dict[str, Tuple[float, float]] = {
    "tier_1_whales": (0.05, 0.35),       # (Fraction of Wallets, Fraction of Pool)
    "tier_2_active": (0.25, 0.45),
    "tier_3_casual": (0.70, 0.20),
}


def estimate_participant_count(
    tvl_usd: float,
    social_hype_index: float,
    is_free: bool = True,
) -> int:
    """
    Estimates the total number of unique wallet participants farming the airdrop.
    Free testnets attract 3x-10x more bots/sybils than capital-required mainnet protocols.
    """
    base_users = 25_000
    
    # Scaling with TVL (if available)
    if tvl_usd > 0:
        tvl_component = min(500_000, int(tvl_usd / 500))  # 1 user per $500 TVL
    else:
        tvl_component = 0
        
    # Scaling with Social Virality
    hype_component = int((social_hype_index / 50.0) ** 1.8 * 40_000)
    
    # Capital friction penalty: Free tasks have much higher raw participation
    friction_multiplier = 3.5 if is_free else 0.8
    
    total_raw = (base_users + tvl_component + hype_component) * friction_multiplier
    return max(5_000, int(total_raw))


def calculate_sybil_adjusted_reward(
    airdrop_pool_usd: float,
    total_participants: int,
    sybil_filter_rate: float = 0.50,
    target_cohort: str = "tier_2_active",
) -> float:
    """
    Calculates the expected airdrop reward ($) for a participant in the specified cohort tier.
    
    Formulation:
    N_effective = N_participants * (1 - Sybil_Rate)
    Reward = (Pool * Tier_Pool_Share) / (N_effective * Tier_Wallet_Share)
    """
    effective_participants = max(100, int(total_participants * (1.0 - sybil_filter_rate)))
    
    cohort_info = TIER_WEIGHTS.get(target_cohort, TIER_WEIGHTS["tier_2_active"])
    wallet_share, pool_share = cohort_info
    
    cohort_wallets = max(1, int(effective_participants * wallet_share))
    cohort_pool_usd = airdrop_pool_usd * pool_share
    
    expected_reward = cohort_pool_usd / cohort_wallets
    return round(expected_reward, 2)
