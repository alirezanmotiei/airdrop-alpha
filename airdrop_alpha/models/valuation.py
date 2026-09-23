"""
Valuation Modeling Engine for AirdropAlpha.
Implements institutional models for Implied Fully Diluted Valuation (FDV)
and Airdrop Pool Sizing based on comparable protocol multiples and VC funding step-ups.
"""

from typing import Dict
from airdrop_alpha.core.models import FundingData, VCTier

# Empirical FDV/TVL Sector Multipliers derived from historical TGE benchmarks
SECTOR_MULTIPLIERS: Dict[str, float] = {
    "L1/L2": 5.5,             # Layer-1 / Layer-2 (e.g. Arbitrum, Optimism, Celestia, Monad)
    "DeFi": 1.6,              # DEXes & Lending (e.g. Uniswap, Aave comps)
    "Liquid Restaking": 2.2,  # LRTs & Restaking (e.g. EigenLayer, EtherFi)
    "DePIN": 4.0,             # Decentralized Physical Infrastructure (e.g. Helium, Render)
    "AI / Crypto": 6.0,       # AI Agents & Decentralized Compute
    "GameFi": 2.5,            # Web3 Gaming & Metaverse
    "SocialFi": 2.0,          # Decentralized Social
    "Infrastructure": 3.8,    # Oracles, Cross-chain, Bridges (e.g. LayerZero, Pyth)
    "Default": 2.0,
}

# Baseline default FDV estimates for unpriced projects based on VC tier
TIER_BASELINE_FDV: Dict[VCTier, float] = {
    VCTier.TIER_1: 450_000_000.0,   # Paradigm/a16z backed typically list at $300M - $1B+ FDV
    VCTier.TIER_2: 120_000_000.0,   # Tier-2 VCs typically list at $80M - $200M FDV
    VCTier.TIER_3: 35_000_000.0,    # Seed/Angel funded typically list at $20M - $50M FDV
    VCTier.UNBACKED: 8_000_000.0,   # Community / stealth projects baseline ~$5M - $15M FDV
}


def estimate_implied_fdv(
    category: str,
    tvl_usd: float,
    funding: FundingData,
    market_bull_multiplier: float = 1.0,
) -> float:
    """
    Estimates the Implied Fully Diluted Valuation ($FDV^*) at Token Generation Event (TGE).
    
    Mathematical Formulation:
    FDV* = w1 * (TVL * Sector_Multiplier) + w2 * (Last_Round_Valuation * Step_Up) + w3 * Baseline_FDV
    """
    sector_mult = SECTOR_MULTIPLIERS.get(category, SECTOR_MULTIPLIERS["Default"])
    
    # 1. Comps via TVL
    tvl_fdv = tvl_usd * sector_mult if tvl_usd > 0 else 0.0
    
    # 2. Comps via VC Valuation Step-up
    # Standard Web3 Series A/B to TGE step-up is 1.4x - 2.5x
    vc_fdv = 0.0
    if funding.last_round_valuation_usd > 0:
        vc_fdv = funding.last_round_valuation_usd * 1.6 * market_bull_multiplier
    elif funding.total_raised_usd > 0:
        # Standard rule of thumb: Total Raised is ~10-15% of implied valuation
        vc_fdv = (funding.total_raised_usd / 0.12) * market_bull_multiplier
        
    # 3. Tier Baseline
    baseline_fdv = TIER_BASELINE_FDV.get(funding.vc_tier, TIER_BASELINE_FDV[VCTier.UNBACKED])
    
    # Weighted synthesis
    if tvl_fdv > 0 and vc_fdv > 0:
        implied_fdv = (0.50 * tvl_fdv) + (0.50 * vc_fdv)
    elif vc_fdv > 0:
        implied_fdv = (0.75 * vc_fdv) + (0.25 * baseline_fdv)
    elif tvl_fdv > 0:
        implied_fdv = (0.70 * tvl_fdv) + (0.30 * baseline_fdv)
    else:
        implied_fdv = baseline_fdv
        
    # Bound within realistic market constraints ($1M minimum)
    return max(implied_fdv, 1_000_000.0)


def calculate_airdrop_pool_value(
    implied_fdv: float,
    community_allocation_pct: float = 0.08,
) -> float:
    """
    Calculates the total dollar value allocated to the airdrop pool.
    Standard community airdrop allocation is 5% to 15% (default 8%).
    """
    pct = max(0.01, min(community_allocation_pct, 0.30))
    return implied_fdv * pct
