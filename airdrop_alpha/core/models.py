"""
Core Data Models for AirdropAlpha.
Strongly-typed Pydantic schemas representing airdrops, task requirements,
cost profiles, financial projections, social sentiment, and risk analysis.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CostTier(str, Enum):
    """
    Classification of capital requirements for airdrop participation.
    """
    FREE_TASKS_ONLY = "100% Free (Task Only)"    # Testnets, faucets, social quests, forms (Zero capital)
    GAS_ONLY = "Gas Only (< $5)"                 # Low-cost L2 transactions (Arbitrum, Base, Linea, Scroll)
    CAPITAL_REQUIRED = "Capital Required"        # Staking, TVL liquidity, or perpetual trading volume


class TaskType(str, Enum):
    TESTNET = "Testnet / Faucet"
    SOCIAL_QUEST = "Social / Quest / Discord"
    MAINNET_TX = "Mainnet Contract Interaction"
    STAKING_TVL = "Staking / Liquidity Provider"
    NODE_VALIDATOR = "Node Running / Verification"
    REFERRAL_INVITE = "Referral / Community Growth"


class VCTier(str, Enum):
    TIER_1 = "Tier-1 VC (Paradigm, a16z, Polychain, Dragonfly, Binance Labs)"
    TIER_2 = "Tier-2 VC (Coinbase, Multicoin, Delphi, Variant, Pantera)"
    TIER_3 = "Tier-3 / Angel / Seed Backed"
    UNBACKED = "Community / Anonymous / Unbacked"


class RiskLevel(str, Enum):
    LOW = "Low Risk (Verified & Backed)"
    MODERATE = "Moderate Risk (Caution on Gas/Time)"
    HIGH = "High Risk (Unverified / Anon)"
    CRITICAL_SCAM = "CRITICAL: Potential Phishing / Drainer"


class TaskRequirement(BaseModel):
    title: str
    description: str = ""
    task_type: TaskType = TaskType.SOCIAL_QUEST
    cost_tier: CostTier = CostTier.FREE_TASKS_ONLY
    is_free: bool = True
    estimated_hours: float = 0.5            # Hours needed to complete
    estimated_gas_usd: float = 0.0          # Estimated gas burn
    required_capital_usd: float = 0.0       # Locked capital (if staking)
    is_recurring: bool = False              # Daily/weekly check-in streak required
    instructions: List[str] = Field(default_factory=list)


class FundingData(BaseModel):
    total_raised_usd: float = 0.0           # Total VC funding in USD
    last_round_valuation_usd: float = 0.0   # Implied valuation at last funding round
    lead_investors: List[str] = Field(default_factory=list)
    vc_tier: VCTier = VCTier.UNBACKED
    funding_rounds_count: int = 0
    notable_backers: List[str] = Field(default_factory=list)


class SocialSentiment(BaseModel):
    reddit_mentions: int = 0
    twitter_mentions: int = 0
    sentiment_score: float = 0.0            # Range: -1.0 (Heavy scam reports) to +1.0 (Massive validation)
    scam_warning_count: int = 0             # Number of comments warning of drainer/scam/fake
    positive_signals: int = 0               # Mentions of confirmed rewards, legit team, easy faucet
    hype_index: float = 50.0                # 0 to 100 virality / community engagement index
    sample_threads: List[Dict[str, str]] = Field(default_factory=list)


class RiskProfile(BaseModel):
    safety_score: float = 50.0              # 0 to 100 (Higher = Safer)
    risk_level: RiskLevel = RiskLevel.MODERATE
    drainer_risk: bool = False              # True if malicious approvals/signatures detected
    is_audited: bool = False
    audit_firms: List[str] = Field(default_factory=list)
    team_doxxed: bool = False
    red_flags: List[str] = Field(default_factory=list)
    safety_strengths: List[str] = Field(default_factory=list)
    sybil_risk_warning: str = "Standard sybil filters apply. Avoid sequential identical transactions."


class FinancialMetrics(BaseModel):
    implied_fdv: float = 0.0                # Estimated Fully Diluted Valuation at TGE ($)
    airdrop_pool_usd: float = 0.0           # Estimated total value of airdrop pool ($)
    expected_reward_usd: float = 0.0        # Expected user allocation ($) for typical active tier
    net_profit_usd: float = 0.0             # Expected reward minus costs (gas + capital opp cost)
    hourly_wage_usd: float = 0.0            # $/hour yield on effort invested (Omega)
    hours_per_10usd: float = 0.0            # Hours needed to earn $10 return (H_10 metric)
    roic_percentage: float = 0.0            # Return on Invested Capital (%)
    alpha_score: float = 0.0                # Composite rank score (0 to 100)


class AirdropProject(BaseModel):
    id: str
    name: str
    slug: str
    source: str = "AirdropAlert"             # AirdropAlert, DefiLlama, Reddit, Twitter
    url: str = ""                            # Source listing URL
    website_url: Optional[str] = None
    whitepaper_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    description: str = ""
    category: str = "DeFi"                   # L1/L2, DeFi, DePIN, AI, GameFi, SocialFi
    chains: List[str] = Field(default_factory=list)
    
    # Capital & Cost Classification
    cost_tier: CostTier = CostTier.FREE_TASKS_ONLY
    is_free: bool = True
    
    # Detailed Attributes
    tasks: List[TaskRequirement] = Field(default_factory=list)
    funding: FundingData = Field(default_factory=FundingData)
    social: SocialSentiment = Field(default_factory=SocialSentiment)
    risk: RiskProfile = Field(default_factory=RiskProfile)
    metrics: FinancialMetrics = Field(default_factory=FinancialMetrics)
    
    # Execution & Guide Steps
    guide_steps: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Direct Participation Portal & Security Verification Report
    direct_portal_url: Optional[str] = None
    url_security: Optional[Dict[str, Any]] = None
    
    # Raw data store for debugging or memo generation
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)
