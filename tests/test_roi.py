import pytest
from airdrop_alpha.models.roi_calculator import (
    calculate_expected_net_profit,
    calculate_labor_metrics,
    calculate_composite_alpha_score,
)


def test_calculate_expected_net_profit():
    # Reward $500, Gas $10, Legit 95%
    enp = calculate_expected_net_profit(
        expected_reward_usd=500.0,
        gas_cost_usd=10.0,
        scam_probability=0.05,
    )
    # 0.95 * 500 - 10 = 475 - 10 = 465
    assert enp == 465.0


def test_calculate_labor_metrics_wage_and_h10():
    net_profit = 300.0
    invested_hours = 2.0
    
    hourly_wage, hours_per_10usd = calculate_labor_metrics(
        net_profit_usd=net_profit,
        invested_hours=invested_hours,
    )
    # $300 / 2 hrs = $150/hr
    assert hourly_wage == 150.0
    # $10 / $150/hr = 0.067 hrs (approx 4 minutes)
    assert hours_per_10usd == 0.07


def test_calculate_labor_metrics_zero_profit():
    hourly_wage, hours_per_10usd = calculate_labor_metrics(
        net_profit_usd=0.0,
        invested_hours=2.0,
    )
    assert hourly_wage == 0.0
    assert hours_per_10usd == 999.0  # infinite time penalty


def test_composite_alpha_score_free_bonus():
    score_free = calculate_composite_alpha_score(
        hourly_wage=50.0,
        safety_score=80.0,
        net_profit=100.0,
        capital_cost=0.0,
        is_free=True,
    )
    assert score_free > 50.0
