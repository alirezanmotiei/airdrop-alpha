import pytest
from airdrop_alpha.core.models import AirdropProject, CostTier, FinancialMetrics, RiskProfile
from airdrop_alpha.ranking.scorer import filter_projects, sort_projects


@pytest.fixture
def sample_projects():
    p1 = AirdropProject(
        id="p1",
        name="Free Testnet Airdrop",
        slug="free-testnet",
        cost_tier=CostTier.FREE_TASKS_ONLY,
        is_free=True,
        metrics=FinancialMetrics(
            hourly_wage_usd=120.0,
            hours_per_10usd=0.08,
            alpha_score=85.0,
        ),
        risk=RiskProfile(safety_score=75.0),
    )
    p2 = AirdropProject(
        id="p2",
        name="Gas Only Bridge",
        slug="gas-only",
        cost_tier=CostTier.GAS_ONLY,
        is_free=False,
        metrics=FinancialMetrics(
            hourly_wage_usd=60.0,
            hours_per_10usd=0.17,
            alpha_score=70.0,
        ),
        risk=RiskProfile(safety_score=60.0),
    )
    p3 = AirdropProject(
        id="p3",
        name="Heavy Staking Vault",
        slug="heavy-staking",
        cost_tier=CostTier.CAPITAL_REQUIRED,
        is_free=False,
        metrics=FinancialMetrics(
            hourly_wage_usd=250.0,
            hours_per_10usd=0.04,
            alpha_score=90.0,
        ),
        risk=RiskProfile(safety_score=88.0),
    )
    return [p1, p2, p3]


def test_filter_free_only(sample_projects):
    free_items = filter_projects(sample_projects, free_only=True)
    assert len(free_items) == 1
    assert free_items[0].id == "p1"
    assert free_items[0].cost_tier == CostTier.FREE_TASKS_ONLY


def test_sort_projects_by_hours_per_10usd(sample_projects):
    # Lowest hours per $10 is best (ascending)
    sorted_items = sort_projects(sample_projects, sort_by="hours_per_10usd")
    # p3 has 0.04 hrs, p1 has 0.08 hrs, p2 has 0.17 hrs
    assert sorted_items[0].id == "p3"
    assert sorted_items[1].id == "p1"
    assert sorted_items[2].id == "p2"


def test_sort_projects_by_hourly_wage(sample_projects):
    # Highest hourly wage first
    sorted_items = sort_projects(sample_projects, sort_by="hourly_wage")
    assert sorted_items[0].id == "p3"  # $250/h
    assert sorted_items[1].id == "p1"  # $120/h
    assert sorted_items[2].id == "p2"  # $60/h
