# Phase 0 Research: Agentic Crypto Risk Manager

This document records the architectural and technology decisions, rationale, trade-offs, and best practices evaluated for the Agentic Crypto Risk Manager.

---

## 1. System Architecture: Monorepo with Next.js & Python FastAPI

### Decision
A decoupled monorepo containing:
- **`frontend/`**: Next.js 14+ (App Router), TypeScript, Vanilla CSS design system with dark mode and progressive disclosure UX.
- **`backend/`**: Python 3.11+ with FastAPI, Pydantic v2, and quantitative numerical libraries (`numpy`, `scipy`, `pandas`).

### Rationale
- **Mathematical Rigor**: Risk calculations—specifically $N \times N$ variance-covariance matrix inversion, parametric and historical Value at Risk (VaR), Expected Shortfall (CVaR), and Black-Scholes Greek sensitivities (Delta, Gamma, Vega)—are native, fast, and numerically stable in Python using `scipy.stats` and vectorized `numpy`.
- **Modern Web3 UX**: Next.js provides the gold standard for Web3 wallet integration, client-side progressive disclosure, and responsive real-time dashboards.
- **Clear Contract Boundary**: Communication between Next.js and FastAPI occurs over strongly-typed RESTful endpoints and OpenAPI/Pydantic schemas.

### Alternatives Considered
- **Pure Next.js / TypeScript**: Implementing matrix algebra, covariance estimation, and Black-Scholes in JavaScript/WebAssembly. Rejected because TypeScript lacks mature, standardized numerical libraries equivalent to `numpy`/`scipy`, increasing the risk of mathematical drift.
- **Pure Python Web Framework (e.g., Django or Reflex)**: Rejected because modern Web3 wallet SDKs (Privy, Wagmi, Viem) have first-class, reliable support exclusively in the React/TypeScript ecosystem.

---

## 2. Storage & Caching: PostgreSQL + TimescaleDB & Redis

### Decision
- **PostgreSQL 16 + TimescaleDB**: Stores user position registries, manual deal blotter records, historical price time-series hypertables, and persisted risk audit reports.
- **Redis 7**: High-speed in-memory cache for live price feeds, active session states, and precomputed $N \times N$ covariance matrices (TTL: 60–300s).

### Rationale
- **Time-Series Optimization**: TimescaleDB hypertables handle high-frequency price history partitioning and efficient aggregation over 90, 180, and 365-day calculation windows.
- **Latency Reduction**: Calculating covariance matrices and VaR across 50+ assets can take 50–200ms; caching computed matrices in Redis allows instant UI updates and fast Copilot tool calling.

### Alternatives Considered
- **Standard PostgreSQL without TimescaleDB**: Rejected because time-series queries over multiple asset daily returns become slow as the historical price table grows beyond hundreds of thousands of rows.
- **MongoDB / Document Store**: Rejected because financial records, trades, and position blotters require ACID transactions and relational integrity.

---

## 3. Non-Custodial Wallet Onboarding & ENS Resolution

### Decision
- **Privy**: Primary wallet authentication layer supporting social login (Google, Twitter, Email) alongside external injected wallets (MetaMask, Rabby, Coinbase Wallet) and embedded wallets.
- **ENS (Ethereum Name Service)**: Client-side resolution using `viem` / `ethers.js` on Ethereum Mainnet to resolve hex addresses into `.eth` handles with avatar support.

### Rationale
- **Constitutional Adherence**: Conforms to Principle I (Non-Custodial by Default). Privy does not custody private keys; keys remain embedded/MPC or in external user extensions.
- **Onboarding Velocity**: Non-crypto native or institutional users can log in via email with an embedded self-custodial wallet, while crypto-native users connect via Rabby/MetaMask.
- **Human-Readable Trust**: Displaying `vitalik.eth` rather than `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` increases user confidence.

---

## 4. Multi-Chain Balance Discovery & Token Indexing

### Decision
- **Primary Source**: The Graph Token API & Subgraphs across EVM chains (Ethereum, Arbitrum, Optimism, Polygon, Base).
- **Secondary / Fallback Source**: 1inch Portfolio / Balance API.

### Rationale
- **Decentralization & Coverage**: The Graph provides indexed ERC-20 balances and protocol liquidity holdings directly from on-chain event logs.
- **Resilience**: If The Graph experiences subgraph synchronization delays or rate limits, the 1inch Portfolio API acts as a seamless secondary aggregator.

---

## 5. Market Pricing, Oracles & Tokenized RWA Proof of Reserve

### Decision
- **Primary Pricing**: Chainlink Data Feeds (ETH/USD, BTC/USD, and top EVM token feeds).
- **Fallback Pricing**: DefiLlama / CoinGecko REST APIs for long-tail crypto assets not yet tracked by Chainlink oracles.
- **Tokenized RWAs**: Chainlink Proof of Reserve (PoR) and NAVLink feeds to fetch verified off-chain collateral and Net Asset Value (NAV) valuations.

### Rationale
- **Data Provenance**: Fulfills Constitution Principle IV. Chainlink oracles provide on-chain cryptographic guarantees of price integrity and timestamps.
- **RWA Transparency**: For tokenized treasuries and credit (e.g., Ondo, Matrixdock, Mountain Protocol), Chainlink PoR verifies that on-chain tokens are 1:1 backed by custodial reserves.
- **Graceful Degradation**: Fallback providers are triggered when an oracle answer is stale ($>3600s$) or unavailable, attaching a `provenance: "fallback"` warning to the valuation.

---

## 6. Mathematical Formulations & Assumptions

### Decision
1. **Reference Benchmark**: Bitcoin ($BTC$) serves as the benchmark index ($I_{ref}$) for systematic risk ($\beta$) and Treynor ratio calculations.
2. **Risk-Free Rate**: $R_f = 0.00\%$ baseline assumption.
3. **Single-Deal Beta**:
   $$\beta_i = \frac{\text{Cov}(R_i, R_{BTC})}{\text{Var}(R_{BTC})}$$
4. **Sharpe & Treynor Ratios**:
   $$\text{Sharpe}_i = \frac{\bar{R}_i - R_f}{\sigma_i}, \quad \text{Treynor}_i = \frac{\bar{R}_i - R_f}{\beta_i}$$
5. **Portfolio Variance-Covariance Matrix**:
   $$\Sigma = \frac{1}{T-1} \sum_{t=1}^T (R_t - \bar{R})(R_t - \bar{R})^T$$
6. **Portfolio Net Greeks**:
   $$\Delta_{net} = \sum_{i=1}^N w_i \Delta_i, \quad \Gamma_{net} = \sum_{i=1}^N w_i \Gamma_i, \quad \nu_{net} = \sum_{i=1}^N w_i \nu_i$$
7. **Value at Risk (VaR) & Expected Shortfall (ES)**:
   - Evaluated at both 95% and 99% confidence over a 1-day horizon.
   - Parametric: $\text{VaR}_\alpha = - (\mu_p + z_\alpha \sigma_p)$, where $z_{0.95} \approx -1.645$, $z_{0.99} \approx -2.326$.
   - Historical: Empirical quantile of past simulated daily portfolio returns.
   - Expected Shortfall: Conditional mean of returns exceeding the VaR threshold:
     $$\text{ES}_\alpha = -\mathbb{E}[R_p \mid R_p \le -\text{VaR}_\alpha]$$

---

## 7. Rebalance Routing & Consent-Gated Architecture

### Decision
- **1inch Fusion API & Uniswap Routing API**: Used strictly to fetch competitive swap routes, quote slippage, gas estimates, and build un-signed transaction calldata.
- **Zero Automated Execution**: The backend or AI copilot CANNOT broadcast transactions. The Next.js frontend presents an interactive modal showing pre-flight impact (risk reduction, costs) and prompts the user's wallet for interactive review and signature.

### Rationale
- Conforms strictly to Constitution Principle II (Read-First, Execute-Only-on-Explicit-Consent). Users maintain complete sovereignty over funds.

---

## 8. Gemini-Powered Chat Copilot & Grounded Function Calling

### Decision
- **Google GenAI SDK (Gemini 1.5 Pro / 2.0 Flash)**: Integrated on the FastAPI backend with structured Tool / Function Calling.
- **Grounded Toolset**:
  1. `get_portfolio_summary()`: Returns total USD value, Net Greeks ($\Delta, \Gamma, \nu$), and portfolio Sharpe/Treynor.
  2. `get_risk_metrics(asset_symbol)`: Returns single-deal Beta vs. BTC, Delta, Volatility, Sharpe, and Treynor.
  3. `get_covariance_correlations()`: Returns pairwise correlations for concentrated asset pairs.
  4. `get_var_report()`: Returns 95% and 99% VaR and Expected Shortfall with tail risk drivers.
  5. `propose_rebalance_plan(target_risk_reduction)`: Returns a mathematically balanced trade proposal with simulated risk metrics.

### Guardrails
- Copilot system instructions enforce:
  1. No transaction signing or automated dispatch.
  2. Always state that all proposals require explicit manual confirmation in the user's wallet.
  3. Ground all quantitative responses strictly in the tool outputs (preventing hallucinated metrics).
