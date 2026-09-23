"""
Unified Aggregator Pipeline for AirdropAlpha.
Fuses data from AirdropAlert, DefiLlama, and Social Intelligence channels,
runs institutional valuation, dilution, and risk engines, and produces the final ranked dataset.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from airdrop_alpha.collectors.airdrop_alert import AirdropAlertCollector
from airdrop_alpha.collectors.defillama import DefiLlamaCollector
from airdrop_alpha.collectors.social_collector import SocialIntelligenceCollector
from airdrop_alpha.collectors.base import logger

from airdrop_alpha.core.models import (
    AirdropProject, CostTier, FundingData, VCTier,
    FinancialMetrics, RiskProfile, TaskRequirement, TaskType
)
from airdrop_alpha.models.valuation import estimate_implied_fdv, calculate_airdrop_pool_value
from airdrop_alpha.models.dilution import estimate_participant_count, calculate_sybil_adjusted_reward
from airdrop_alpha.models.roi_calculator import (
    calculate_expected_net_profit, calculate_labor_metrics, calculate_composite_alpha_score
)
from airdrop_alpha.models.risk_engine import evaluate_risk_profile
from airdrop_alpha.models.url_verifier import verify_portal_url


class AirdropAggregator:
    def __init__(self):
        self.alert_collector = AirdropAlertCollector()
        self.llama_collector = DefiLlamaCollector()
        self.social_collector = SocialIntelligenceCollector()

    def run_pipeline(self, use_cache: bool = True) -> List[AirdropProject]:
        """
        Executes the entire intelligence pipeline and returns fully evaluated AirdropProjects.
        """
        logger.info("[Aggregator] Starting quantitative aggregation pipeline...")
        
        # 1. Fetch raw data from providers
        alert_items = self.alert_collector.collect(use_cache=use_cache)
        llama_items = self.llama_collector.collect(use_cache=use_cache)
        social_data = self.social_collector.collect(use_cache=use_cache)
        
        projects: List[AirdropProject] = []
        seen_slugs = set()
        
        # 2. Process AirdropAlert listings
        for item in alert_items:
            slug = item.get("slug", "")
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            
            # Map cost tier
            cost_tier_val = item.get("cost_tier", CostTier.FREE_TASKS_ONLY.value)
            cost_tier = CostTier(cost_tier_val)
            is_free = (cost_tier == CostTier.FREE_TASKS_ONLY)
            
            # Funding data
            lead_vcs = item.get("lead_investors", [])
            vc_tier_val = item.get("vc_tier", VCTier.UNBACKED.value)
            funding = FundingData(
                total_raised_usd=15_000_000.0 if lead_vcs else 0.0,
                last_round_valuation_usd=80_000_000.0 if lead_vcs else 0.0,
                lead_investors=lead_vcs,
                vc_tier=VCTier(vc_tier_val),
            )
            
            # Social Sentiment from Reddit/Twitter
            social = self.social_collector.get_sentiment_for_project(item.get("name", ""), slug)
            
            # Evaluate Risk Profile
            risk = evaluate_risk_profile(
                name=item.get("name", ""),
                description=item.get("description", ""),
                funding=funding,
                social=social,
                audit_mentions=[],
                requires_approval=not is_free,
            )
            
            # Valuation & Dilution Calculations
            category = item.get("category", "DeFi")
            implied_fdv = estimate_implied_fdv(category=category, tvl_usd=0.0, funding=funding)
            airdrop_pool = calculate_airdrop_pool_value(implied_fdv=implied_fdv)
            
            participants = estimate_participant_count(
                tvl_usd=0.0,
                social_hype_index=social.hype_index,
                is_free=is_free
            )
            expected_reward = calculate_sybil_adjusted_reward(
                airdrop_pool_usd=airdrop_pool,
                total_participants=participants,
                sybil_filter_rate=0.50,
            )
            
            # Labor & Cost Profile
            # Free tasks take ~1.2 hours on average, $0 gas
            # Gas tasks take ~1.8 hours, $4 gas
            # Capital tasks take ~2.5 hours, $15 gas, $200 capital
            if cost_tier == CostTier.FREE_TASKS_ONLY:
                est_hours = 1.2
                est_gas = 0.0
                capital_locked = 0.0
            elif cost_tier == CostTier.GAS_ONLY:
                est_hours = 1.8
                est_gas = 4.0
                capital_locked = 0.0
            else:
                est_hours = 2.5
                est_gas = 12.0
                capital_locked = 250.0
                
            net_profit = calculate_expected_net_profit(
                expected_reward_usd=expected_reward,
                gas_cost_usd=est_gas,
                locked_capital_usd=capital_locked,
                scam_probability=0.02 if risk.safety_score > 60 else 0.15,
            )
            hourly_wage, hours_per_10usd = calculate_labor_metrics(
                net_profit_usd=net_profit,
                invested_hours=est_hours,
            )
            
            alpha_score = calculate_composite_alpha_score(
                hourly_wage=hourly_wage,
                safety_score=risk.safety_score,
                net_profit=net_profit,
                capital_cost=est_gas + capital_locked,
                is_free=is_free,
            )
            
            metrics = FinancialMetrics(
                implied_fdv=implied_fdv,
                airdrop_pool_usd=airdrop_pool,
                expected_reward_usd=expected_reward,
                net_profit_usd=net_profit,
                hourly_wage_usd=hourly_wage,
                hours_per_10usd=hours_per_10usd,
                roic_percentage=round((net_profit / max(1.0, est_gas + capital_locked)) * 100, 1),
                alpha_score=alpha_score,
            )
            
            task_req = TaskRequirement(
                title=f"Complete {item.get('name')} tasks",
                description=item.get("description", ""),
                task_type=TaskType.SOCIAL_QUEST if is_free else TaskType.MAINNET_TX,
                cost_tier=cost_tier,
                is_free=is_free,
                estimated_hours=est_hours,
                estimated_gas_usd=est_gas,
                required_capital_usd=capital_locked,
                instructions=item.get("guide_steps", []),
            )
            
            portal_url = item.get("website_url") or item.get("url") or ""
            url_security = verify_portal_url(portal_url, item.get("name", ""))
            
            # If high risk phishing detected, penalize safety and flag drainer risk
            if not url_security.is_safe:
                risk.red_flags.extend(url_security.warnings)
                risk.safety_score = max(5.0, risk.safety_score - 30.0)
                if url_security.is_punycode or url_security.has_homoglyphs:
                    risk.drainer_risk = True

            project = AirdropProject(
                id=item["id"],
                name=item["name"],
                slug=slug,
                source="AirdropAlert",
                url=item.get("url", ""),
                website_url=item.get("website_url"),
                whitepaper_url=item.get("whitepaper_url"),
                direct_portal_url=portal_url,
                url_security=url_security.model_dump(),
                description=item.get("description", ""),
                category=category,
                chains=item.get("chains", ["Multi-Chain"]),
                cost_tier=cost_tier,
                is_free=is_free,
                tasks=[task_req],
                funding=funding,
                social=social,
                risk=risk,
                metrics=metrics,
                guide_steps=item.get("guide_steps", []),
                tags=[category, cost_tier.value],
            )
            projects.append(project)

        # 3. Process DefiLlama high-TVL tokenless protocols (top 20)
        for llama in llama_items[:20]:
            slug = llama.get("slug", "")
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            
            tvl = llama.get("tvl_usd", 0.0)
            category = llama.get("category", "DeFi")
            cost_tier_val = llama.get("cost_tier", CostTier.CAPITAL_REQUIRED.value)
            cost_tier = CostTier(cost_tier_val)
            is_free = False
            
            funding = FundingData(
                total_raised_usd=tvl * 0.08,
                last_round_valuation_usd=tvl * 1.5,
                lead_investors=["DeFi Syndicate", "Crypto Native Fund"],
                vc_tier=VCTier.TIER_2 if tvl > 50_000_000 else VCTier.TIER_3,
            )
            
            social = self.social_collector.get_sentiment_for_project(llama.get("name", ""), slug)
            
            risk = evaluate_risk_profile(
                name=llama.get("name", ""),
                description=llama.get("description", ""),
                funding=funding,
                social=social,
                audit_mentions=llama.get("audit_firms", []),
                requires_approval=True,
            )
            
            implied_fdv = estimate_implied_fdv(category=category, tvl_usd=tvl, funding=funding)
            airdrop_pool = calculate_airdrop_pool_value(implied_fdv=implied_fdv, community_allocation_pct=0.10)
            
            participants = estimate_participant_count(tvl_usd=tvl, social_hype_index=social.hype_index, is_free=False)
            expected_reward = calculate_sybil_adjusted_reward(
                airdrop_pool_usd=airdrop_pool,
                total_participants=participants,
                sybil_filter_rate=0.45,
            )
            
            est_hours = 2.0
            est_gas = 8.0
            capital_locked = 500.0
            
            net_profit = calculate_expected_net_profit(
                expected_reward_usd=expected_reward,
                gas_cost_usd=est_gas,
                locked_capital_usd=capital_locked,
                scam_probability=0.01 if risk.safety_score > 70 else 0.08,
            )
            hourly_wage, hours_per_10usd = calculate_labor_metrics(
                net_profit_usd=net_profit,
                invested_hours=est_hours,
            )
            alpha_score = calculate_composite_alpha_score(
                hourly_wage=hourly_wage,
                safety_score=risk.safety_score,
                net_profit=net_profit,
                capital_cost=est_gas + capital_locked,
                is_free=False,
            )
            
            metrics = FinancialMetrics(
                implied_fdv=implied_fdv,
                airdrop_pool_usd=airdrop_pool,
                expected_reward_usd=expected_reward,
                net_profit_usd=net_profit,
                hourly_wage_usd=hourly_wage,
                hours_per_10usd=hours_per_10usd,
                roic_percentage=round((net_profit / max(1.0, est_gas + capital_locked)) * 100, 1),
                alpha_score=alpha_score,
            )
            
            task_req = TaskRequirement(
                title=f"Deposit & interact with {llama.get('name')}",
                description=f"Interact with {llama.get('name')} contract to qualify for potential governance token retroactive allocation.",
                task_type=TaskType.STAKING_TVL if tvl > 10_000_000 else TaskType.MAINNET_TX,
                cost_tier=cost_tier,
                is_free=False,
                estimated_hours=est_hours,
                estimated_gas_usd=est_gas,
                required_capital_usd=capital_locked,
                instructions=[
                    f"Visit official portal: {llama.get('website_url')}",
                    "Connect Web3 wallet on supported chains",
                    "Supply liquidity or execute volume swaps to accumulate retroactive points",
                ],
            )
            
            portal_url = llama.get("website_url") or llama.get("url") or ""
            url_security = verify_portal_url(portal_url, llama.get("name", ""))

            project = AirdropProject(
                id=llama["id"],
                name=llama["name"],
                slug=slug,
                source="DefiLlama",
                url=llama.get("url", ""),
                website_url=llama.get("website_url"),
                twitter_handle=llama.get("twitter_handle"),
                direct_portal_url=portal_url,
                url_security=url_security.model_dump(),
                description=llama.get("description", ""),
                category=category,
                chains=llama.get("chains", []),
                cost_tier=cost_tier,
                is_free=False,
                tasks=[task_req],
                funding=funding,
                social=social,
                risk=risk,
                metrics=metrics,
                guide_steps=task_req.instructions,
                tags=[category, "High TVL", cost_tier.value],
            )
            projects.append(project)

        logger.info(f"[Aggregator] Successfully aggregated and evaluated {len(projects)} total projects.")
        return projects
