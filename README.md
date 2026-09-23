<h1 align="center">AirdropAlpha</h1>

<p align="center">
  <strong>Institutional-Grade Quantitative Airdrop Scouting, Valuation & Risk Evaluation Engine</strong><br>
  <em>A Quantitative Intelligence Framework for Web3 Airdrop Opportunities, Labor Economics, and Phishing Defense</em><br>
  <strong>Author:</strong> Alireza Najafi Motiei (<a href="https://github.com/alirezanmotiei">@alirezanmotiei</a>)
</p>

<p align="center">
  <a href="https://python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?style=flat&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://docs.astral.sh/uv/"><img src="https://img.shields.io/badge/uv-Package%20Manager-DE5FE9.svg?style=flat&logo=astral&logoColor=white" alt="uv"></a>
  <a href="https://pytest.org/"><img src="https://img.shields.io/badge/Tests-24%2F24%20Passing-brightgreen.svg?style=flat&logo=pytest&logoColor=white" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat" alt="License: MIT"></a>
  <a href="https://github.com/alirezanmotiei/airdrop-alpha/actions"><img src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF.svg?style=flat&logo=github-actions&logoColor=white" alt="CI"></a>
</p>

---

## 📖 Executive Summary

**AirdropAlpha** is an institutional-grade quantitative research and intelligence system engineered to systematically scout, value, risk-audit, and rank Web3 cryptocurrency airdrops. In decentralized finance (DeFi), participants frequently suffer from asymmetric information, disguised phishing links ("wallet drainers"), and sub-optimal capital/time allocation on low-yield farming programs.

AirdropAlpha addresses these challenges through a mathematically rigorous multi-stage pipeline:
1. **Multi-Source Intelligence Ingestion**: Live automated scraping and normalization of active airdrops from AirdropAlert RSS, over 3,800 tokenless protocols from DefiLlama, and community discussion feeds from Reddit (`r/CryptoAirdrop`, `r/airdrop`, `r/CryptoCurrency`).
2. **Quantitative Valuation & Labor Economics Modeling**: Formulates an Implied Fully Diluted Valuation ($FDV^*$) using sector comps and VC step-ups, models participant dilution using Sybil-discounted Pareto power-law distributions, and derives the **Hourly Return on Effort ($\Omega_{\text{effort}}$)** and the **Hours required per \$10 net reward ($H_{10}$)**.
3. **URL Deep Inspection & Phishing Defense Shield**: Deep-packet analysis of action URLs to detect punycode attacks, homoglyph spoofing (e.g. Cyrillic characters), suspicious drainer keywords, and abused disposable TLDs.
4. **Multi-Factor Risk Scoring**: Evaluates VC tiering (Paradigm, a16z, Binance Labs), smart contract audits (OpenZeppelin, Trail of Bits), and social sentiment NLP.
5. **Interactive Dual-Interface Delivery**: Delivers insights via an interactive **Rich Terminal CLI** and a modern **Glassmorphism Web Dashboard** featuring a **Bilingual (English & Persian) Engine**, a **Personal Farming ROI Simulator**, and 1-Click **1-Page Investment Memo Generation**.

---

## 📐 Mathematical & Quantitative Formulation

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          AirdropAlpha Quantitative Pipeline                            │
├─────────────────────────┬────────────────────────────┬─────────────────────────────────┤
│   Multi-Source Scout    │   Valuation & Security     │       Decision & Ranking        │
│                         │                            │                                 │
│  • AirdropAlert Live    │  • Implied FDV Model       │  • 100% Free Hunter Filter      │
│  • DefiLlama (3800+)    │  • Pareto Dilution Tiers   │  • Hourly Wage ($/Hour)         │
│  • Reddit Social NLP    │  • URL Phishing & Homoglyph│  • Hours per $10 Return (H10)   │
│  • Enterprise Proxy     │  • Multi-Factor Safety     │  • Composite Alpha Score (0-100)│
└─────────────────────────┴────────────────────────────┴─────────────────────────────────┘
```

### 1. Implied Fully Diluted Valuation ($FDV^*$)
$$\text{FDV}^* = w_1 \cdot \left(\text{TVL} \times \mu_{\text{sector}}\right) + w_2 \cdot \left(V_{\text{last\_round}} \times (1 + \beta_{\text{market}})\right) + w_3 \cdot \text{FDV}_{\text{tier\_baseline}}$$
Where $\mu_{\text{sector}}$ represents empirical FDV/TVL multiples derived from historical Token Generation Events (TGE):
- Layer-1 / Layer-2 ($5.5\times$)
- AI / Crypto Compute ($6.0\times$)
- DePIN Infrastructure ($4.0\times$)
- Liquid Restaking ($2.2\times$)
- DeFi DEX / Lending ($1.6\times$)

### 2. Airdrop Pool Valuation ($V_{\text{pool}}$)
$$V_{\text{pool}} = \text{FDV}^* \times \alpha_{\text{community}}$$
Where $\alpha_{\text{community}} \in [0.05, 0.15]$ represents the typical community token allocation share.

### 3. Sybil-Adjusted Pareto Cohort Dilution
Effective eligible participants are modeled by stripping out automated sybil clusters:
$$N_{\text{eff}} = N_{\text{participants}} \times (1 - \delta_{\text{sybil}})$$
Allocations are distributed across non-linear Pareto tiers:
- **Tier 1 (Whales / Core Protocol Contributors - Top 5%)**: Receives 35% of the pool.
- **Tier 2 (Active Power Users / Consistent Farmers - Next 25%)**: Receives 45% of the pool.
- **Tier 3 (Casual / Free Quest Hunters - Remaining 70%)**: Receives 20% of the pool.

$$E[R_{\text{tier}}] = \frac{V_{\text{pool}} \times W_{\text{tier}}}{N_{\text{eff}} \times S_{\text{tier}}}$$

### 4. Expected Net Profit ($ENP$) & Hourly Wage on Effort ($\Omega_{\text{effort}}$)
$$\text{ENP} = \left(P_{\text{legit}} \times E[R]\right) - \left(C_{\text{gas}} + C_{\text{capital\_opp}}\right)$$
$$\Omega_{\text{effort}} = \frac{\text{ENP}}{T_{\text{hours}}} \quad [\$/\text{hour}]$$

### 5. Time-Value Metric: Hours per \$10 Net Return ($H_{10}$)
$$H_{10} = \frac{10}{\Omega_{\text{effort}}} = \frac{10 \times T_{\text{hours}}}{\text{ENP}} \quad [\text{hours}]$$
*A lower $H_{10}$ indicates superior labor efficiency. If $H_{10} < 0.2\text{ hours}$ (< 12 minutes per \$10), the program is designated as **Tier-A Alpha**.*

### 6. Anti-Phishing & Homograph URL Verification
The verification engine inspects direct action URLs across five security dimensions:
$$S_{\text{url}} = \mathbb{I}(\text{HTTPS}) \cdot \left[1 - \mathbb{I}(\text{Punycode}) - \mathbb{I}(\text{Homoglyph}) - \lambda_{\text{phish}} \cdot \text{Keywords}\right]$$
Flagged domains containing Cyrillic character substitutions (e.g., `xn--...` or `\u0430`) are immediately quarantined as **Critical Phishing Alerts**.

---

## 🌟 Key Capabilities & Features

* **🎯 Zero-Capital / 100% Free Hunter Mode**: 1-click filter separating 100% zero-cost tasks (faucets, testnets, social quests) from capital-intensive staking or gas-heavy transactions.
* **🛡️ Deep URL Verification Shield**: Automatic verification of official protocol links against DefiLlama registries to protect users from malicious wallet drainers.
* **🗣️ Reddit & Twitter Social Sentiment**: Automated NLP scanner detecting community scam alerts (`drainer`, `scam`, `fake`, `phishing`) vs positive validation (`legit`, `confirmed`, `binance labs`).
* **🌍 Bilingual Engine (English & Persian)**: Dynamic RTL/LTR toggle supporting Persian (Vazirmatn typography) and English with bidirectional text isolation.
* **🧮 Personal Farming ROI Simulator**: Interactive dashboard tool simulating expected monthly returns based on available weekly hours and burner wallet counts.
* **📄 Automated 1-Page Investment Memo**: Generates institutional research memos in Markdown and HTML with anti-sybil self-check guidelines.
* **🌐 Enterprise Proxy Support**: Out-of-the-box compatibility with HTTP, HTTPS, and SOCKS5 proxies (`HTTP_PROXY`, `ALL_PROXY`, or CLI flags) for unrestricted worldwide access.

---

## 🏗️ Project Architecture

```
airdrop_alpha/
├── .github/
│   └── workflows/
│       └── tests.yml            # Automated CI pipeline (Python 3.10, 3.11, 3.12)
├── airdrop_alpha/
│   ├── core/
│   │   ├── config.py            # Settings, proxy configuration, network parameters
│   │   └── models.py            # Pydantic schemas (AirdropProject, FinancialMetrics, RiskProfile)
│   ├── collectors/
│   │   ├── base.py              # BaseCollector with caching & proxy-aware HTTP client
│   │   ├── airdrop_alert.py     # Live RSS parser for active airdrops & step-by-step guides
│   │   ├── defillama.py         # Tokenless protocol & TVL collector
│   │   ├── social_collector.py  # Reddit & Twitter discussion monitor
│   │   └── aggregator.py        # Central data fusion and quantitative evaluation pipeline
│   ├── models/
│   │   ├── valuation.py         # Implied FDV & airdrop pool sizing models
│   │   ├── dilution.py          # Sybil discount & Pareto distribution calculations
│   │   ├── roi_calculator.py    # Labor yield ($/hr) and hours-per-$10 (H10) math
│   │   ├── sentiment.py         # NLP community sentiment & scam alert detector
│   │   ├── risk_engine.py       # Multi-factor safety & VC syndicate scoring
│   │   └── url_verifier.py      # Anti-phishing, punycode, and homograph detection
│   ├── ranking/
│   │   └── scorer.py            # Multi-criteria alpha ranking & zero-capital filtering
│   ├── reporting/
│   │   └── memo.py              # Bilingual 1-Page Investment Memo generator
│   ├── ui/
│   │   ├── cli.py               # Rich interactive terminal interface
│   │   └── web/
│   │       ├── app.py           # FastAPI web backend
│   │       └── templates/
│   │           └── index.html   # Glassmorphism frontend with Alpine.js & Tailwind CSS
│   └── main.py                  # Unified CLI / Web entrypoint
├── tests/                       # Automated Pytest suite (24 tests, 100% green)
│   ├── test_models.py
│   ├── test_valuation.py
│   ├── test_roi.py
│   ├── test_sentiment.py
│   ├── test_risk_engine.py
│   ├── test_scorer.py
│   ├── test_url_verifier.py
│   └── test_memo.py
├── pyproject.toml               # Modern packaging configuration
└── LICENSE                      # MIT License
```

---

## 🚀 Quickstart & Reproduction

### 1. Installation
Clone the repository and install dependencies using `uv` (recommended) or standard `pip`:

```bash
git clone https://github.com/alirezanmotiei/airdrop-alpha.git
cd airdrop-alpha
uv sync --extra dev
```

### 2. Terminal CLI Dashboard
```bash
# Display top 100% Free / Zero-Capital airdrops sorted by $/hour return
uv run python -m airdrop_alpha.main cli --free-only --sort hourly_wage

# View top 10 safest opportunities with lowest hours per $10
uv run python -m airdrop_alpha.main cli --sort hours_per_10usd --limit 10

# Generate 1-Page Investment Memo for a target protocol
uv run python -m airdrop_alpha.main memo "Pond AI"
```

### 3. Modern Glassmorphism Web Dashboard
```bash
uv run python -m airdrop_alpha.main web --port 8000
```
Navigate to `http://localhost:8000` to access the interactive dashboard, toggle between **English** and **فارسی**, simulate personal ROI, and download CSV data exports.

### 4. Running Verification Tests
```bash
uv run pytest tests/ -v
```

---

## 🌐 Enterprise Proxy Configuration

For environments with restricted network conditions or geo-fencing:

```bash
# SOCKS5 Proxy Configuration (e.g. v2ray / Shadowsocks)
export ALL_PROXY="socks5://127.0.0.1:10808"

# HTTP/HTTPS Proxy Configuration (e.g. Clash / Charles)
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"

# Or pass directly via CLI
uv run python -m airdrop_alpha.main cli --proxy http://127.0.0.1:7890
```

---

## 📚 Citation

If you find this research framework or implementation useful in your academic or quantitative work, please cite it as:

```bibtex
@software{motiei2026airdropalpha,
  author       = {Alireza Najafi Motiei},
  title        = {{AirdropAlpha: Institutional-Grade Quantitative Airdrop Scouting & Valuation Engine}},
  year         = {2026},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/alirezanmotiei/airdrop-alpha}},
}
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
