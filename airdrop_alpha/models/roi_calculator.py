"""
ROI and Labor Opportunity Cost Calculator for AirdropAlpha.
Implements Expected Value (EV), Hourly Wage on Effort ($/hour),
and the proprietary Hours-per-$10 Return Metric (H_10).
"""

from typing import Tuple


def calculate_expected_net_profit(
    expected_reward_usd: float,
    gas_cost_usd: float = 0.0,
    locked_capital_usd: float = 0.0,
    lockup_months: float = 3.0,
    risk_free_apy: float = 0.05,
    scam_probability: float = 0.05,
) -> float:
    """
    Computes Expected Net Profit (ENP) incorporating gas burn, opportunity cost of locked capital,
    and protocol legitimacy probability.
    
    ENP = (P_legit * Expected_Reward) - (Gas_Cost + Capital_Opportunity_Cost)
    """
    p_legit = max(0.0, 1.0 - scam_probability)
    capital_opp_cost = locked_capital_usd * risk_free_apy * (lockup_months / 12.0)
    total_cost = gas_cost_usd + capital_opp_cost
    
    net_profit = (p_legit * expected_reward_usd) - total_cost
    return round(net_profit, 2)


def calculate_labor_metrics(
    net_profit_usd: float,
    invested_hours: float,
) -> Tuple[float, float]:
    """
    Calculates:
    1. Hourly Wage on Effort (Omega): Return in $/hour
    2. Hours needed per $10 profit (H_10): Exactly how many hours must be invested to extract $10 net profit.
    
    Returns:
        (hourly_wage_usd, hours_per_10usd)
    """
    safe_hours = max(0.05, invested_hours)
    
    # 1. Hourly Wage on Effort
    hourly_wage = net_profit_usd / safe_hours
    
    # 2. Hours per $10 Net Return (H_10)
    if net_profit_usd <= 0:
        # If profit is zero or negative, return infinite time penalty
        hours_per_10usd = 999.0
    else:
        # H_10 = 10 / (Profit / Hours) = (10 * Hours) / Profit
        hours_per_10usd = round(10.0 / hourly_wage, 2)
        
    return round(hourly_wage, 2), hours_per_10usd


def calculate_composite_alpha_score(
    hourly_wage: float,
    safety_score: float,
    net_profit: float,
    capital_cost: float,
    is_free: bool = True,
) -> float:
    """
    Calculates the Composite Alpha Score (0 to 100) combining:
    - Yield on labor (hourly wage vs standard $25/hr benchmark)
    - Safety and scam protection
    - Capital efficiency (bonus for 100% Free zero-capital farming)
    """
    # 1. Labor efficiency factor (capped at 4x benchmark)
    norm_wage = min(4.0, max(0.0, hourly_wage / 25.0))
    labor_factor = (norm_wage / 4.0) * 100.0
    
    # 2. Safety factor (0 to 100)
    safety_factor = max(0.0, min(100.0, safety_score))
    
    # 3. Capital efficiency factor
    if is_free or capital_cost <= 0:
        capital_efficiency = 100.0  # Perfect capital score for 100% Free
    else:
        roic = net_profit / max(1.0, capital_cost)
        capital_efficiency = min(100.0, max(10.0, roic * 15.0))
        
    # Multi-attribute weighting: 40% Labor Return, 35% Safety, 25% Capital Efficiency
    alpha_score = (0.40 * labor_factor) + (0.35 * safety_factor) + (0.25 * capital_efficiency)
    return round(max(0.0, min(100.0, alpha_score)), 1)
