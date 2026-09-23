# 🚀 AirdropAlpha: Institutional-Grade Airdrop Scouting & Quantitative Valuation Engine

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Clean Architecture](https://img.shields.io/badge/architecture-clean-brightgreen.svg)]()

> **AirdropAlpha** is an institutional-grade crypto intelligence and quantitative research engine designed to scout, evaluate, risk-score, and rank Web3 airdrops. Powered by quantitative financial models (Implied FDV, Sybil dilution, Hourly Return $\Omega_{\text{effort}}$, Hours-per-\$10 metric $H_{10}$) and a multi-source intelligence pipeline (AirdropAlert live RSS, DefiLlama tokenless protocols, Reddit and Twitter social sentiment).

---

## 🌟 Key Highlights

- **🎯 Zero-Capital / 100% Free Hunter Focus**: Dedicated 1-click filtering (`--free-only`) separating 100% zero-cost tasks from gas-only or capital-intensive staking opportunities.
- **📊 Quantitative Financial Modeling**:
  - Implied FDV calculation based on comparable protocol multiples and VC funding step-ups.
  - Sybil-adjusted cohort dilution using Pareto power-law distributions.
  - Hourly Return on Effort ($\$/\text{hour}$) and Hours needed per \$10 reward ($H_{10}$).
- **🛡️ Multi-Factor Safety & Drainer Shield**:
  - Scam & Wallet Drainer detection (Permit2 heuristic checks, unverified contracts, fake social handles).
  - Smart contract audit scoring (OpenZeppelin, Trail of Bits, Spearbit, CertiK).
  - VC Syndicate Tiering (Tier-1: Paradigm, a16z, Polychain, Binance Labs vs unbacked).
- **🗣️ Social Intelligence & Community Sentiment**:
  - Live scraping of Reddit discussion boards (`r/CryptoAirdrop`, `r/airdrop`, `r/CryptoCurrency`) and Twitter sentiment.
  - Automated detection of community warning alerts (`scam`, `drainer`, `fake`, `phishing`) vs validation (`legit`, `confirmed`).
- **🖥️ Dual Interfaces**:
  - **Rich Interactive CLI**: Full color-coded terminal tables, badges, and instant sorting.
  - **Modern Glassmorphism Web Dashboard**: Responsive FastAPI + Tailwind CSS UI with live search, sliders, and 1-Page Investment Memos.
- **🌐 Global Enterprise Proxy Support**: Out-of-the-box support for HTTP, HTTPS, and SOCKS5 proxies (`HTTP_PROXY`, `ALL_PROXY`, or CLI flags) to ensure seamless data scraping across any network or region.

---

## 📐 Mathematical Formulation

### 1. Implied FDV Model ($FDV^*$)
$$\text{FDV}^* = w_1 \cdot \left(\text{TVL} \times \mu_{\text{sector}}\right) + w_2 \cdot \left(V_{\text{last\_round}} \times (1 + \beta_{\text{market}})\right) + w_3 \cdot \text{FDV}_{\text{peer\_median}}$$

### 2. Expected Net Profit ($ENP$) & Hourly Wage ($\Omega_{\text{effort}}$)
$$\text{ENP} = \left(P_{\text{legit}} \times E[R]\right) - \left(C_{\text{gas}} + C_{\text{capital}}\right)$$
$$\Omega_{\text{effort}} = \frac{\text{ENP}}{T_{\text{hours}}} \quad [\$/\text{hour}]$$

### 3. Hours Required per \$10 Return ($H_{10}$)
$$H_{10} = \frac{10}{\Omega_{\text{effort}}} \quad [\text{hours}]$$

---

## 🛠️ Quickstart

### 1. Installation
```bash
git clone https://github.com/your-username/airdrop-alpha.git
cd airdrop-alpha
uv sync
```

### 2. Run CLI Scanner
```bash
# Filter 100% Free / Zero-Capital airdrops, sorted by $/hour return
uv run python -m airdrop_alpha.main cli --free-only --sort hourly_wage

# View top 10 safest airdrops
uv run python -m airdrop_alpha.main cli --sort safety_score --limit 10

# Generate 1-Page Investment Memo for a specific project
uv run python -m airdrop_alpha.main memo "Midas Markets"
```

### 3. Launch Modern Web Dashboard
```bash
uv run python -m airdrop_alpha.main web --port 8000
```
Open your browser at `http://localhost:8000`.

---

## 🌐 Enterprise Proxy Configuration

For global developers or environments with network restrictions:
```bash
# SOCKS5 Proxy
export ALL_PROXY="socks5://127.0.0.1:10808"

# HTTP/HTTPS Proxy
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
```
Or specify directly via CLI:
```bash
uv run python -m airdrop_alpha.main cli --proxy http://127.0.0.1:7890
```

---

## 📄 License
MIT License. Built for Web3 researchers, quantitative analysts, and independent airdrop hunters.
