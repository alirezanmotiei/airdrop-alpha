import pytest
from airdrop_alpha.core.models import (
    AirdropProject, CostTier, TaskType, TaskRequirement,
    FundingData, VCTier, FinancialMetrics, RiskProfile
)


def test_model_cost_tier_classification():
    task_free = TaskRequirement(
        title="Faucet claim",
        cost_tier=CostTier.FREE_TASKS_ONLY,
        is_free=True,
        estimated_hours=0.5,
    )
    assert task_free.is_free is True
    assert task_free.cost_tier == CostTier.FREE_TASKS_ONLY

    task_gas = TaskRequirement(
        title="L2 Bridge",
        cost_tier=CostTier.GAS_ONLY,
        is_free=False,
        estimated_gas_usd=2.5,
    )
    assert task_gas.is_free is False
    assert task_gas.cost_tier == CostTier.GAS_ONLY


def test_airdrop_project_instantiation():
    project = AirdropProject(
        id="test-1",
        name="Arbitrum Season 3",
        slug="arbitrum-season-3",
        cost_tier=CostTier.FREE_TASKS_ONLY,
        is_free=True,
        category="L1/L2",
        chains=["Arbitrum"],
    )
    assert project.id == "test-1"
    assert project.name == "Arbitrum Season 3"
    assert project.is_free is True
    assert project.metrics.hourly_wage_usd == 0.0
