# Quickstart Validation Guide: Agentic Crypto Risk Manager

This guide walks through end-to-end local environment setup and validation scenarios proving each user story and quantitative risk calculation.

---

## 1. Prerequisites

- **Node.js**: v18.18+ or v20+
- **Python**: v3.11 or higher with `pip` / `uv`
- **Docker & Docker Compose**: For PostgreSQL (TimescaleDB) and Redis
- **API Keys**:
  - `PRIVY_APP_ID` & `PRIVY_APP_SECRET`: [Privy Dashboard](https://dashboard.privy.io/)
  - `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com/)
  - `THE_GRAPH_API_KEY`: [The Graph Studio](https://thegraph.com/studio/)
  - `ONEINCH_API_KEY`: [1inch Developer Portal](https://portal.1inch.dev/)

---

## 2. Environment Setup

### 2.1 Start Local Infrastructure (Postgres/TimescaleDB + Redis)
```bash
docker run -d --name risk-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres timescale/timescaledb:latest-pg16
docker run -d --name risk-redis -p 6379:6379 redis:7-alpine
```

### 2.2 Backend Setup (FastAPI)
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### 2.3 Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
# Running on http://localhost:3000
```

---

## 3. End-to-End Validation Scenarios

### Scenario 1: Non-Custodial Login & ENS Resolution
1. Navigate to `http://localhost:3000`.
2. Click **Connect Wallet**. Select Privy (Email / Embedded Wallet) or MetaMask / Rabby.
3. **Expected Outcome**:
   - Connection established without asking for private keys.
   - If connected address has an ENS record (e.g. `vitalik.eth`), the header displays the ENS handle with fallback to `0xd8...045`.
   - Backend registers session via `POST /api/v1/auth/session`.

### Scenario 2: Multi-Chain Holdings Discovery & Manual Blotter Entry
1. View the **Positions Blotter**.
2. Trigger **Sync On-Chain Balances**.
   - Verified via `POST /api/v1/portfolio/{address}/sync`.
   - Tokens on Ethereum, Arbitrum, Optimism, and Base appear with quantities and USD valuations.
3. Click **Add Manual Position**:
   - Asset Name: `ONDO_USDY`
   - Trade Date: `2026-08-15`
   - Side: `Buy`
   - Trade Type: `Spot`
   - Asset Class: `Real-World Asset (RWA)`
   - Settlement Date: `2026-08-15`
   - Venue: `Ondo Finance`
   - Quantity: `10000`
   - Cost Basis: `$1.00`
4. **Expected Outcome**:
   - Manual deal is saved (`POST /api/v1/blotter/{address}/deals`).
   - Consolidated portfolio total USD valuation immediately updates.

### Scenario 3: Single-Deal Risk Analytics Inspection
1. Click on any asset row (e.g., `ETH`).
2. **Expected Outcome**:
   - Drawer/modal renders single-deal analytics:
     - **Beta ($\beta$)**: Calculated using Bitcoin as the reference index.
     - **Delta ($\Delta$)**: Directional sensitivity.
     - **Volatility ($\sigma$)**: 90-day annualized volatility.
     - **Standard Deviation**: Historical dispersion.
     - **Sharpe Ratio**: Risk-adjusted return assuming $R_f = 0$.
     - **Treynor Ratio**: Risk-adjusted return relative to Beta ($R_f = 0$).

### Scenario 4: Whole-Portfolio Greeks & Variance-Covariance Matrix
1. Navigate to the **Portfolio Risk** tab.
2. **Expected Outcome**:
   - Executive header displays:
     - **Net Delta ($\Delta_{net}$)**
     - **Net Vega ($\nu_{net}$)**
     - **Net Gamma ($\Gamma_{net}$)**
     - **Portfolio Sharpe Ratio ($R_f=0$)**
     - **Portfolio Treynor Ratio ($R_f=0$)**
   - Interactive $N \times N$ Variance-Covariance Matrix displays pairwise covariances and heat-mapped correlation coefficients.

### Scenario 5: Risk Report Generation & Consent-Gated Rebalancing
1. Click **Generate Risk Report**.
2. **Expected Outcome**:
   - Report displays 1-day **95% VaR**, **99% VaR**, and **Expected Shortfall (ES / CVaR)**.
   - Recommended rebalancing actions appear (e.g., "Trim concentrated ETH position to reduce VaR by $1,420").
3. Click **Review Rebalance Quote**:
   - 1inch Fusion / Uniswap quote is fetched (`POST /api/v1/rebalance/quote`).
   - Modal displays expected slippage, gas cost, and new simulated risk metrics.
4. Click **Execute in Wallet**:
   - Wallet extension triggers an interactive transaction prompt.
   - **Verification**: If user rejects the wallet prompt, zero transactions execute; state remains unchanged.

### Scenario 6: Gemini Grounded Copilot Chat
1. Open the **AI Risk Copilot** drawer.
2. Type: `"Explain why my portfolio VaR is so high and what asset is driving it."`
3. **Expected Outcome**:
   - Gemini invokes `get_portfolio_summary`, `get_covariance_correlations`, and `get_tail_risk_report`.
   - Copilot provides grounded explanation referencing exact portfolio numbers and suggests rebalancing actions with an explicit disclaimer that execution requires manual user wallet sign-off.
