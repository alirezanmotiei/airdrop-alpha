"""
Institutional 1-Page Investment Memo Generator for AirdropAlpha.
Generates comprehensive research memos in both English and Persian (Farsi),
with strict BiDi directionality protection.
"""

from typing import Optional
from airdrop_alpha.core.models import AirdropProject, CostTier


def generate_investment_memo(project: AirdropProject, lang: str = "en") -> str:
    """
    Renders an institutional 1-Page Investment Memo for the specified airdrop project.
    Supports 'en' (English, LTR) and 'fa' (Persian, RTL).
    """
    p = project
    m = p.metrics
    r = p.risk
    f = p.funding
    s = p.social

    if lang == "fa":
        return _generate_memo_persian(p, m, r, f, s)
    else:
        return _generate_memo_english(p, m, r, f, s)


def _generate_memo_english(p, m, r, f, s) -> str:
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

    return f"""# 📄 INSTITUTIONAL AIRDROP MEMORANDUM: {p.name.upper()}

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
| **Hourly Wage on Effort ($\\\\Omega$)** | **${m.hourly_wage_usd:,.2f} / hr** | Effective yield per 1 hour of manual task labor |
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

## 5. DIRECT PORTAL & DOMAIN VERIFICATION AUDIT
- **Direct Action URL**: `{p.direct_portal_url or p.website_url or 'N/A'}`
- **Domain Verification Status**: **{(p.url_security or {}).get('status', 'Unverified')}**
- **SSL / HTTPS Security**: {'✅ Secured (HTTPS Protocol Verified)' if (p.url_security or {}).get('is_https') else '🚨 INSECURE HTTP DETECTED'}
- **Anti-Phishing / Homograph Check**: {'✅ Clean Domain (No Punycode / IDN Spoofing)' if not (p.url_security or {}).get('is_punycode') else '🚨 CRITICAL: Punycode homograph attack detected!'}
- **Verification Badges**: {', '.join((p.url_security or {}).get('verification_badges', ['Standard Web3 Listing']))}
- **Security Guidance**: {(p.url_security or {}).get('guidance', 'Always verify SSL lock icon and official handles.')}

---

## 6. SECURITY & DRAINER SHIELD ASSESSMENT
- **Safety Score**: **{r.safety_score:.1f} / 100** ({r.risk_level.value})
- **Wallet Drainer Risk**: {'🚨 CRITICAL DRAINER RISK' if r.drainer_risk else '🛡️ No active drainer signatures detected'}

### Institutional Strengths:
{strengths_md}

### Risk Flags & Vigilance:
{red_flags_md}

### 🛡️ Anti-Sybil Self-Check:
{r.sybil_risk_warning}

---

## 7. STEP-BY-STEP PARTICIPATION GUIDE
{steps_md}
"""


def _generate_memo_persian(p, m, r, f, s) -> str:
    if p.cost_tier == CostTier.FREE_TASKS_ONLY:
        cost_badge = "🟢 **[۱۰۰٪ رایگان - بدون نیاز به سرمایه اولیه]**"
    elif p.cost_tier == CostTier.GAS_ONLY:
        cost_badge = "🟡 **[صرفاً کارمزد تراکنش (< ۵ دلار) - بدون نیاز به واریز]**"
    else:
        cost_badge = "🔴 **[نیازمند سرمایه اولیه - استیکینگ / نقدینگی]**"

    lead_vcs = ", ".join(f.lead_investors) if f.lead_investors else "حمایت جامعه / اعلام‌نشده"
    audits = ", ".join(r.audit_firms) if r.audit_firms else "بدون ممیزی رسمی / در انتظار اعتبارسنجی"

    steps_md = ""
    if p.guide_steps:
        for idx, step in enumerate(p.guide_steps, 1):
            steps_md += f"{idx}. {step}\n"
    else:
        steps_md = "۱. ورود به وب‌سایت رسمی پروژه.\n۲. اتصال کیف‌پول و انجام تسک‌های اولیه شبکه اجتماعی.\n"

    red_flags_md = ""
    if r.red_flags:
        for rf in r.red_flags:
            red_flags_md += f"- ⚠️ {rf}\n"
    else:
        red_flags_md = "- ریسک حادی شناسایی نشد. ریسک‌های معمول قراردادهای هوشمند پابرجاست.\n"

    strengths_md = ""
    if r.safety_strengths:
        for st in r.safety_strengths:
            strengths_md += f"- ✅ {st}\n"
    else:
        strengths_md = "- برنامه تشویقی استاندارد در حوزه وب۳.\n"

    assessment_tag = (
        "🟢 **فرصت طلایی (بازدهی ساعتی عالی)**"
        if m.hours_per_10usd < 1.0
        else "🟡 **متوسط (نسبت زمان به سود منطقی)**"
        if m.hours_per_10usd < 4.0
        else "🔴 **احتیاط (زمان زیاد در ازای سود اندک)**"
    )

    return f"""<div dir="rtl">

# 📄 یادداشت تحلیلی سرمایه‌گذاری ایردراپ: {p.name}

**نام پروتکل**: {p.name}  
**دسته‌بندی**: {p.category} | **شبکه‌ها**: {', '.join(p.chains)}  
**درگاه رسمی**: {p.website_url or p.url or 'نامشخص'}  
**وایت‌پیپر و مستندات**: {p.whitepaper_url or 'نامشخص'}  
**وضعیت سرمایه ورودی**: {cost_badge}

---

## ۱. خلاصه اجرایی و ارزش پیشنهادی
{p.description}

- **منبع داده**: {p.source}
- **سطح هزینه**: {p.cost_tier.value}
- **سد ورود مالی**: {'۰ دلار (کاملاً رایگان با انجام تسک)' if p.is_free else 'نیازمند کارمزد شبکه یا سپرده‌گذاری'}

---

## ۲. مدل کمی‌سازی ارزش و بازده اقتصادی

| شاخص مالی | مقدار تحلیلی | توضیح و مبنای محاسبه |
| :--- | :--- | :--- |
| **ارزش‌گذاری ضمنی ($FDV^*$)** | **${m.implied_fdv:,.0f}** | تخمین ارزش بازار در زمان عرضه توکن بر پایه ضریب TVL و راندهای خطرپذیر |
| **ارزش استخر ایردراپ** | **${m.airdrop_pool_usd:,.0f}** | کل ارزش دلاری تخمینی توزیع برای جامعه |
| **پاداش انتظاری هر کاربر ($EV$)** | **${m.expected_reward_usd:,.2f}** | پاداش تخمینی برای یک کاربر فعال واجد شرایط |
| **سود خالص انتظاری ($ENP$)** | **${m.net_profit_usd:,.2f}** | سود خالص پس از کسر کارمزد گس و هزینه فرصت سرمایه |
| **بازدهی ساعتی کار ($\\\\Omega$)** | **${m.hourly_wage_usd:,.2f} / hr** | دستمزد معادل بر حسب دلار در هر ۱ ساعت زمان صرف‌شده |
| **شاخص زمان به ازای ۱۰ دلار ($H_{{10}}$)** | **{m.hours_per_10usd:.2f} ساعت** | چند ساعت باید وقت بگذارید تا ۱۰ دلار سود خالص بگیرید |
| **امتیاز آلفا (Alpha Score)** | **{m.alpha_score:.1f} از ۱۰۰** | رتبه اعتباری و جذابیت کلی فرصت |

> 💡 **ارزیابی زمان-ارزش سرمایه‌گذاری**:  
> با بازدهی **${m.hourly_wage_usd:.2f}** در هر ساعت، برای به دست آوردن ۱۰ دلار سود به **{m.hours_per_10usd:.2f} ساعت** کار نیاز است.  
> وضعیت: {assessment_tag}

---

## ۳. پشتوانه سرمایه‌گذاران و ممیزی‌ها
- **سطح سرمایه‌گذاران (VC Tier)**: {f.vc_tier.value}
- **کل سرمایه جذب‌شده**: ${f.total_raised_usd:,.0f}
- **صندوق‌های پیشرو**: {lead_vcs}
- **ممیزی قراردادهای هوشمند**: {audits}

---

## ۴. هوش اجتماعی و نظرات جامعه ردیت و توییتر
- **تعداد ارجاعات**: {s.reddit_mentions} تاپیک ردیت | {s.twitter_mentions} سیگنال توییتر
- **شاخص احساسات جامعه ($S_{{social}}$)**: **{s.sentiment_score:+.2f}** (از ۱.۰- تا ۱.۰+)
- **شاخص هایپ و توجه کاربران**: **{s.hype_index:.1f} از ۱۰۰**
- **هشدارهای اسکم/درینر در کامنت‌ها**: **{s.scam_warning_count}** مورد شناسایی شد

---

## ۵. اعتبارسنجی اصالت آدرس اینترنتی و بررسی ضد فیشینگ (URL Security Audit)
- **لینک مستقیم و رسمی ورود**: `{p.direct_portal_url or p.website_url or 'نامشخص'}`
- **وضعیت اعتبارسنجی دامنه**: **{(p.url_security or {}).get('status', 'در انتظار اعتبارسنجی')}**
- **امنیت پروتکل SSL / HTTPS**: {'✅ کاملاً ایمن (پروتکل HTTPS تأیید شد)' if (p.url_security or {}).get('is_https') else '🚨 ناامن: وبسایت از پروتکل ناامن HTTP استفاده می‌کند!'}
- **بررسی حمله هم‌نگاره و پونی‌کد (Punycode/Homograph)**: {'✅ دامنه تمیز است (بدون حروف جعلی یا کاراکترهای مشابه)' if not (p.url_security or {}).get('is_punycode') else '🚨 خطر فوری: حمله پونی‌کد و جعل حروف شناسایی شد!'}
- **نشان‌های اعتبارسنجی دامنه**: {', '.join((p.url_security or {}).get('verification_badges', ['ثبت‌شده در منابع وب۳']))}
- **توصیه امنیتی**: {(p.url_security or {}).get('guidance', 'همواره آدرس را با توییتر رسمی پروژه چک کنید.')}

---

## ۶. ارزیابی ریسک و سپر ضد درینر (Drainer Shield)
- **امتیاز امنیت**: **{r.safety_score:.1f} از ۱۰۰** ({r.risk_level.value})
- **خطر درینر کیف‌پول**: {'🚨 هشدار: ریسک درخواست پرمیشن‌های مخرب' if r.drainer_risk else '🛡️ بدون امضای مخرب'}

### نقاط قوت امنیتی:
{strengths_md}

### هشدارهای ریسک:
{red_flags_md}

### 🛡️ چک‌لیست جلوگیری از شناسایی به عنوان سیبیل (Anti-Sybil):
{r.sybil_risk_warning}

---

## ۷. راهنمای گام‌به‌گام مشارکت
{steps_md}

</div>
"""
