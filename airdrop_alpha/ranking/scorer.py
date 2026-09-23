"""
Multi-Criteria Scoring, Filtering & Ranking Engine for AirdropAlpha.
Supports 1-click Zero-Capital Free Hunter filtering and multi-dimensional sorting.
"""

from typing import List, Optional
from airdrop_alpha.core.models import AirdropProject, CostTier


def filter_projects(
    projects: List[AirdropProject],
    free_only: bool = False,
    min_safety_score: float = 0.0,
    category: Optional[str] = None,
    chain: Optional[str] = None,
    min_hourly_wage: float = 0.0,
    max_hours_per_10usd: Optional[float] = None,
) -> List[AirdropProject]:
    """
    Applies user filters to the airdrop dataset.
    """
    filtered = []
    for p in projects:
        # Zero-Capital / 100% Free Hunter Filter
        if free_only and p.cost_tier != CostTier.FREE_TASKS_ONLY:
            continue
            
        # Minimum Safety Filter
        if p.risk.safety_score < min_safety_score:
            continue
            
        # Category Filter
        if category and category.lower() != "all":
            if category.lower() not in p.category.lower():
                continue
                
        # Blockchain Filter
        if chain and chain.lower() != "all":
            if not any(chain.lower() in c.lower() for c in p.chains):
                continue
                
        # Hourly Wage Filter
        if p.metrics.hourly_wage_usd < min_hourly_wage:
            continue
            
        # Hours per $10 Filter
        if max_hours_per_10usd is not None:
            if p.metrics.hours_per_10usd > max_hours_per_10usd:
                continue
                
        filtered.append(p)
        
    return filtered


def sort_projects(
    projects: List[AirdropProject],
    sort_by: str = "alpha_score",
    ascending: bool = False,
) -> List[AirdropProject]:
    """
    Sorts airdrops by institutional metrics:
    - alpha_score: Composite multi-factor score
    - hourly_wage: Highest $/hour return on effort
    - hours_per_10usd: Least hours required per $10 profit (ascending default)
    - safety_score: Lowest risk / highest VC backing & audit
    - expected_reward: Highest total expected payout ($)
    - implied_fdv: Largest protocol scale
    """
    key_map = {
        "alpha_score": lambda p: p.metrics.alpha_score,
        "hourly_wage": lambda p: p.metrics.hourly_wage_usd,
        "hours_per_10usd": lambda p: p.metrics.hours_per_10usd,
        "safety_score": lambda p: p.risk.safety_score,
        "expected_reward": lambda p: p.metrics.expected_reward_usd,
        "implied_fdv": lambda p: p.metrics.implied_fdv,
    }
    
    sort_func = key_map.get(sort_by, key_map["alpha_score"])
    
    # Note: For hours_per_10usd, smaller is better, so default is ascending
    if sort_by == "hours_per_10usd":
        # Sort lowest time first
        return sorted(projects, key=sort_func, reverse=ascending)
    else:
        # Sort highest value first
        return sorted(projects, key=sort_func, reverse=not ascending)
