# Implementation Plan: Agentic Crypto Risk Manager

**Branch**: `001-agentic-risk-manager` | **Date**: 2026-09-07 | **Spec**: [spec.md](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/specs/001-agentic-risk-manager/spec.md)

**Input**: Feature specification from `specs/001-agentic-risk-manager/spec.md`

## Summary

Build an institutional-grade, non-custodial crypto portfolio risk manager using a Next.js (TypeScript) frontend and a Python FastAPI quantitative risk backend. The application enables multi-chain wallet login (Privy, World ID, ENS), auto-discovery of on-chain holdings (The Graph Token API, 1inch API), and manual deal logging (Spot, RWAs with Proof of Reserve, Perpetual futures). The backend computes single-deal metrics (Beta vs. BTC, Delta, Volatility, StdDev, Sharpe, Treynor with $R_f=0$) and whole-portfolio aggregates (Net Greeks: Delta/Vega/Gamma, Variance-Covariance matrix, Parametric & Historical VaR, and Expected Shortfall). An integrated Gemini-powered chat copilot provides grounded natural language explanations of risk numbers and proposes rebalancing routes via 1inch Fusion and Uniswap, strictly gated behind explicit user wallet confirmation and signature (zero automated execution).

## Technical Context

**Language/Version**: TypeScript 5.4+ (Node.js 20+) for Frontend; Python 3.11+ for Backend

**Primary Dependencies**:
- *Frontend*: Next.js 14+ (App Router), `@privy-io/react-auth`, `viem`, `wagmi`, Lucide Icons, Vanilla CSS design system
- *Backend*: `fastapi`, `uvicorn`, `pydantic-v2`, `numpy`, `scipy`, `pandas`, `asyncpg`, `redis-py`, `google-genai` (Gemini SDK), `httpx`

**Storage**:
- PostgreSQL 16 with **TimescaleDB** extension for user position blotters, historical price time-series hypertables, and persisted risk audit reports.
- **Redis 7** for caching live price quotes, session metadata, and precomputed $N \times N$ variance-covariance matrices (60–300s TTL).

**Testing**:
- *Backend*: `pytest`, `pytest-asyncio`, `pytest-mock`, numerical analytical test fixtures for covariance matrices and Black-Scholes formulas.
- *Frontend*: `vitest`, React Testing Library, mock Web3 wallet providers.

**Target Platform**: Modern web browsers (Chrome, Brave, Firefox, Edge, Safari); Dockerized deployment on Linux.

**Project Type**: Decoupled Web Application (`frontend/` + `backend/`).

**Performance Goals**:
- High-dimension $N \times N$ variance-covariance matrix computation in $<200\text{ms}$ for up to 50 assets.
- Single-deal risk analytics computed in $<100\text{ms}$.
- Full portfolio VaR and Expected Shortfall report generation in $<2\text{s}$.
- Live price updates with cached redis response in $<20\text{ms}$.

**Constraints**:
- **Strict Non-Custodial Integrity**: Zero private key storage or transmission.
- **Consent-Gated Execution**: 1inch and Uniswap integrations are read-only for quote generation; transactions MUST be approved and signed interactively in the user's wallet.
- **Grounded AI Copilot**: The Gemini Copilot cannot sign transactions or call execution endpoints; all responses are grounded in tool outputs.
- **Pricing & Zero-Valuation Guardrail**: Crypto holdings are priced via CoinGecko API (supporting optional `COINGECKO_API_KEY` with batched lookups). Any token missing or unlisted defaults to $0.00 unit price and $0.00 total value with provenance `unpriced_zero`; such assets are strictly excluded from weighted portfolio risk calculations (Beta, Greeks, Covariance, Sharpe) to eliminate zero-division distortions.

**Scale/Scope**: EVM chains (Ethereum, Arbitrum, Optimism, Base, Polygon); 3 asset classes (Spot Crypto, Tokenized RWAs, Perpetuals).

## Constitution Check

*GATE: All gates evaluated against the Project Constitution (v1.1.0).*

| Principle | Check / Gate | Status | Notes |
| :--- | :--- | :--- | :--- |
| **I. Non-Custodial by Default** | System never holds private keys; uses Privy, World ID, and public indexers | **PASS** | Keys remain strictly in user wallets / MPC; The Graph queries read-only data. |
| **II. Read-First, Consent-Only** | Rebalancing suggestions require explicit interactive wallet signature | **PASS** | 1inch / Uniswap used strictly for quotes; execution requires interactive client signing. |
| **III. Deterministic Risk Math** | Single-deal and portfolio formulas are versioned, unit-tested, with $R_f=0$ and BTC benchmark | **PASS** | Built in Python with `numpy`/`scipy` with exact formulas codified in tests. |
| **IV. Data Provenance & Degradation**| Source timestamps tracked for CoinGecko, Chainlink, and CEX/DEX feeds; graceful degradation | **PASS** | Oracle feeds maintain staleness checks; unlisted assets fallback to $0.00 with explicit `unpriced_zero` provenance tags. |
| **V. Pluggable Adapters (EVM)** | Core domain model decoupled from blockchain; EVM execution scope | **PASS** | Python domain models are agnostic; adapter modules handle chain-specific RPCs and APIs. |
| **VI. Observability & Auditability** | Reports expose intermediate covariance calculations and explainable rebalance steps | **PASS** | Full matrix snapshots and rebalancing risk deltas stored in `risk_reports`. |
| **VII. Progressive Disclosure UX** | Executive health and net Greeks upfront; drill-down to blotter and covariance matrix | **PASS** | Designed into Next.js dashboard hierarchy. |

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-risk-manager/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── api-spec.yaml    # OpenAPI 3.1 REST API specification
│   └── gemini-tools.json # Gemini Copilot function calling schemas
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
agentic_risk_manager/
├── backend/                          # Python FastAPI Quantitative Backend
│   ├── src/
│   │   ├── api/                      # REST API endpoints (v1)
│   │   │   ├── auth.py               # Wallet session & ENS resolution
│   │   │   ├── portfolio.py          # Unified positions & auto-sync
│   │   │   ├── blotter.py            # Manual deal blotter CRUD
│   │   │   ├── risk.py               # Single-deal & portfolio risk endpoints
│   │   │   ├── rebalance.py          # 1inch & Uniswap quote router
│   │   │   └── copilot.py            # Gemini streaming chat with tool calling
│   │   ├── core/                     # Core business logic & models
│   │   │   ├── config.py             # App settings & environment variables
│   │   │   └── database.py           # PostgreSQL/TimescaleDB & Redis connections
│   │   ├── math/                     # Deterministic Quantitative Risk Library
│   │   │   ├── beta.py               # Beta vs. BTC benchmark calculations
│   │   │   ├── greeks.py             # Black-Scholes & synthetic Greeks (Delta, Gamma, Vega)
│   │   │   ├── covariance.py         # N x N variance-covariance matrix & correlations
│   │   │   ├── ratios.py             # Sharpe & Treynor ratios (Rf = 0)
│   │   │   └── tail_risk.py          # Parametric & Historical VaR, Expected Shortfall (CVaR)
│   │   ├── services/                 # External service adapters
│   │   │   ├── indexer.py            # The Graph Token API & 1inch fallback
│   │   │   ├── oracles.py            # CoinGecko API Pricing Oracle (batched/cached), Chainlink & PoR/NAVLink
│   │   │   ├── swaps.py              # 1inch Fusion & Uniswap quote clients
│   │   │   └── gemini.py             # Google GenAI grounded copilot client
│   │   ├── models/                   # Pydantic & SQLAlchemy / asyncpg schemas
│   │   │   ├── entities.py           # Database table mappings
│   │   │   └── schemas.py            # Request/response DTOs
│   │   └── main.py                   # FastAPI application entry point
│   ├── tests/                        # Backend test suites
│   │   ├── unit/                     # Math & formula correctness tests
│   │   │   ├── test_beta.py
│   │   │   ├── test_greeks.py
│   │   │   ├── test_covariance.py
│   │   │   └── test_tail_risk.py
│   │   └── integration/              # API & adapter integration tests
│   │       ├── test_portfolio_api.py
│   │       └── test_rebalance_quote.py
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # Backend Dockerfile
│
├── frontend/                         # Next.js TypeScript Frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router pages
│   │   │   ├── layout.tsx            # Root layout with Privy & Web3 providers
│   │   │   ├── page.tsx              # Executive Risk Dashboard
│   │   │   ├── blotter/page.tsx      # Multi-asset trade blotter & manual entry
│   │   │   ├── correlation/page.tsx  # Interactive Variance-Covariance Matrix view
│   │   │   └── reports/page.tsx      # Risk Report generator & Rebalance wizard
│   │   ├── components/               # UI components
│   │   │   ├── layout/               # Header, wallet status, ENS badge, navigation
│   │   │   ├── dashboard/            # Health score, Net Greeks summary cards
│   │   │   ├── blotter/              # Positions table, manual deal modal form
│   │   │   ├── risk/                 # Single-deal analytics drawer, VaR chart
│   │   │   ├── rebalance/            # Rebalance proposal card & pre-flight modal
│   │   │   └── copilot/              # AI Risk Copilot chat drawer
│   │   ├── hooks/                    # Custom React hooks (usePortfolio, useRisk, useCopilot)
│   │   ├── lib/                      # Viem clients, API fetchers, math formatting
│   │   └── styles/                   # Curated dark-mode design system & animations
│   ├── package.json                  # Frontend dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   └── next.config.mjs               # Next.js configuration
│
├── docker-compose.yml                # Local orchestration (TimescaleDB, Redis, API, UI)
└── README.md                         # Project documentation
```

**Structure Decision**: A decoupled web application structure (`frontend/` + `backend/`) was selected because quantitative portfolio risk calculations (matrix decomposition, Black-Scholes, VaR, Expected Shortfall) require the stability and vectorization of Python (`numpy`/`scipy`), while modern Web3 wallet onboarding (Privy, ENS, viem) requires a responsive Next.js/React environment.

## Complexity Tracking

*No constitutional violations identified. Standard non-custodial and deterministic architecture maintained.*
