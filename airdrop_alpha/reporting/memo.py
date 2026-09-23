"""
Institutional 1-Page Investment Memo Generator for AirdropAlpha.
Generates comprehensive research memos in Markdown and HTML.
"""

from typing import Optional
from airdrop_alpha.core.models import AirdropProject, CostTier


def generate_investment_memo(project: AirdropProject) -> str:
    """
    Renders an institutional 1-Page Investment Memo for the specified airdrop project.
    """
    p = project
    m = p.metrics
    r = p.risk
    f = p.funding
    s = p.social
    
    # Cost Badge
    if p.cost_tier == CostTier.FREE_TASKS_ONLY:
        cost_badge = "🟢 **[100% FREE - ZERO INITIAL CAPITAL]**"
    elif p.cost_tier == CostTier.GAS_ONLY:
        cost_badge = "🟡 **[GAS ONLY (< $5) - NO DEPOSIT REQUIRED]**"
    else:
        cost_badge = "🔴 **[CAPITAL REQUIRED - STAKING / LIQUIDITY]**"
        
    lead_vcs = ", ".join(f.lead_investors) if f.lead_investors else "Community Backed / Undisclosed"
    audits = ", ".join(r.audit_firms) if r.audit_firms else "Unaudited / Pending Verification"
    
    steps_md = ""
    if p.guide_steps:
        for idx, step in enumerate(p.guide_steps, 1):
            steps_md += f"{idx}. {step}\n"
    else:
        steps_md = "1. Visit official platform link.\n2. Complete community quests and connect Web3 wallet.\n"
        
    red_flags_md = ""
    if r.red_flags:
        for rf in r.red_flags:
            red_flags_md += f"- ⚠️ {rf}\n"
    else:
        red_flags_md = "- None detected. Standard operational risks apply.\n"
        
    strengths_md = ""
    if r.safety_strengths:
        for st in r.safety_strengths:
            strengths_md += f"- ✅ {st}\n"
    else:
        strengths_md = "- Standard Web3 community incentive program.\n"

    memo = f"""# 📄 INSTITUTIONAL AIRDROP MEMORANDUM: {p.name.upper()}

**Target Protocol**: {p.name}  
**Category**: {p.category} | **Blockchains**: {', '.join(p.chains)}  
**Official Portal**: {p.website_url or p.url or 'N/A'}  
**Whitepaper / Docs**: {p.whitepaper_url or 'N/A'}  
**Capital Friction**: {cost_badge}

---

## 1. EXECUTIVE SUMMARY & VALUE PROPOSITION
{p.description}

- **Primary Source**: {p.source}
- **Cost Classification**: {p.cost_tier.value}
- **Initial Capital Barrier**: {'$0 (Zero initial funds needed)' if p.is_free else 'Requires Gas / Liquidity'}

---

## 2. QUANTITATIVE VALUATION & RETURN MODEL

| Financial Metric | Analytical Value | Description |
| :--- | :--- | :--- |
| **Implied FDV ($FDV^*$)** | **${m.implied_fdv:,.0f}** | Estimated market cap at TGE based on sector comps & VC rounds |
| **Airdrop Pool Value** | **${m.airdrop_pool_usd:,.0f}** | Total dollar value earmarked for community distribution |
| **Expected User Reward ($EV$)** | **${m.expected_reward_usd:,.2f}** | Estimated reward for an active eligible wallet |
| **Expected Net Profit ($ENP$)** | **${m.net_profit_usd:,.2f}** | Net gain after deducting gas burn & capital opportunity costs |
| **Hourly Wage on Effort ($\Omega$)** | **${m.hourly_wage_usd:,.2f} / hr** | Effective yield per 1 hour of manual task labor |
| **Hours per $10 Return ($H_{{10}}$)** | **{m.hours_per_10usd:.2f} Hours** | Exactly how much time you must invest to earn $10 profit |
| **Composite Alpha Score** | **{m.alpha_score:.1f} / 100** | Multi-attribute institutional opportunity rank |

> 💡 **Time-Value Assessment**:
> At **${m.hourly_wage_usd:.2f}/hr**, this opportunity requires **{m.hours_per_10usd:.2f} hours** of labor per $10 return.
> {'🟢 **RECOMMENDED**: High labor efficiency!' if m.hours_per_10usd < 1.0 else '🟡 **MODERATE**: Reasonable time commitment.' if m.hours_per_10usd < 4.0 else '🔴 **CAUTION**: High labor requirement for modest payout.'}

---

## 3. VC SYNDICATE & FUNDING BACKING
- **VC Syndicate Tier**: {f.vc_tier.value}
- **Total Institutional Capital Raised**: ${f.total_raised_usd:,.0f}
- **Lead Investors & Backers**: {lead_vcs}
- **Contract Audits**: {audits}

---

## 4. SOCIAL INTELLIGENCE & COMMUNITY SENTIMENT
- **Reddit & Twitter Mentions**: {s.reddit_mentions} Reddit threads | {s.twitter_mentions} Twitter signals
- **Community Sentiment Score ($S_{{social}}$)**: **{s.sentiment_score:+.2f}** (Scale: -1.0 to +1.0)
- **Community Hype & Virality Index**: **{s.hype_index:.1f} / 100**
- **Community Scam / Drainer Warnings**: **{s.scam_warning_count}** alerts detected

---

## 5. SECURITY & DRAINER SHIELD ASSESSMENT
- **Safety Score**: **{r.safety_score:.1f} / 100** ({r.risk_level.value})
- **Wallet Drainer Risk**: {'🚨 CRITICAL DRAINER RISK' if r.drainer_risk else '🛡️ No active drainer signatures detected'}

### Institutional Strengths:
{strengths_md}

### Risk Flags & Vigilance:
{red_flags_md}

### 🛡️ Anti-Sybil Self-Check:
{r.sybil_risk_warning}

---

## 6. STEP-BY-STEP PARTICIPATION GUIDE
{steps_md}
"""
    return memo
