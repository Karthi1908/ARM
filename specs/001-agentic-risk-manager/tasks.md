# Tasks: Agentic Crypto Risk Manager

**Input**: Design documents from `specs/001-agentic-risk-manager/` (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md)

**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/

**Tests**: Unit tests for quantitative risk formulas (Beta, Greeks, Covariance, VaR, CVaR) and integration tests for external balance discovery/quote routers are included in Phase 8.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Exact file paths are included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Monorepo initialization, Docker orchestration, and dependency scaffolding

- [X] T001 Initialize monorepo directory layout with `backend/` and `frontend/` per implementation plan
- [X] T002 [P] Configure Docker Compose orchestration for PostgreSQL 16 (TimescaleDB) and Redis 7 in `docker-compose.yml`
- [X] T003 [P] Initialize Python FastAPI backend environment, dependencies, and virtualenv in `backend/requirements.txt`
- [X] T004 [P] Initialize Next.js 14+ TypeScript project, dependencies, and configuration in `frontend/package.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure, database engines, schemas, and styling tokens that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Configure application configuration and environment variable validation in `backend/src/core/config.py`
- [X] T006 [P] Implement PostgreSQL connection pool and TimescaleDB hypertable initialization in `backend/src/core/database.py`
- [X] T007 [P] Implement Redis caching client for live prices, quotes, and computed matrices in `backend/src/core/redis_client.py`
- [X] T008 [P] Implement database entities and SQLAlchemy / asyncpg schema mappings in `backend/src/models/entities.py`
- [X] T009 [P] Implement Pydantic v2 DTO schemas for API request and response validation in `backend/src/models/schemas.py`
- [X] T010 Implement core FastAPI application with CORS and error handling middleware in `backend/src/main.py`
- [X] T011 [P] Configure Privy React Provider and Wagmi/Viem Web3 configuration in `frontend/src/app/providers.tsx`
- [X] T012 [P] Implement CSS design tokens, dark mode palette, and typography system in `frontend/src/styles/theme.css`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Multi-Chain Wallet Discovery & Unified Holdings (Priority: P1) 🎯 MVP

**Goal**: Non-custodial wallet onboarding via Privy/WorldID, ENS handle resolution, multi-chain ERC-20 balance discovery via The Graph Token API (with 1inch fallback), and unified USD valuation.

**Independent Test**: Connect an EVM wallet (or enter public address); verify that balances across Ethereum, Arbitrum, Optimism, and Base are automatically indexed, valued in USD, and rendered with the user's ENS name.

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement ENS reverse resolution and session handler in `backend/src/api/auth.py`
- [X] T014 [P] [US1] Implement Chainlink price feed reader and CoinGecko fallback service with timestamped provenance in `backend/src/services/oracles.py`
- [X] T015 [US1] Implement multi-chain token balance fetcher via The Graph Token API with 1inch fallback in `backend/src/services/indexer.py`
- [X] T016 [US1] Implement portfolio balance discovery and sync endpoint `POST /api/v1/portfolio/{wallet_address}/sync` in `backend/src/api/portfolio.py`
- [X] T017 [P] [US1] Implement navigation header with Privy login modal, wallet status, and ENS badge in `frontend/src/components/layout/Header.tsx`
- [X] T018 [US1] Implement unified holdings table with chain badges, token quantities, and USD valuations in `frontend/src/components/dashboard/HoldingsTable.tsx`
- [X] T019 [US1] Implement executive dashboard page integrating wallet connection and holdings discovery in `frontend/src/app/page.tsx`

**Checkpoint**: User Story 1 is fully functional as a standalone MVP.

---

## Phase 4: User Story 2 - Multi-Asset Manual Deal Blotter (Priority: P1)

**Goal**: Enable users to record, edit, and delete off-chain CEX trades, OTC contracts, Tokenized RWAs (with Chainlink Proof of Reserve / NAVLink verification), and Perpetual futures.

**Independent Test**: Add a manual deal (e.g. ONDO USDY, trade date, buy/sell, spot, settlement date, Ondo venue); verify that the deal is persisted, valued in USD, verified via Proof of Reserve, and blended into the consolidated portfolio.

### Implementation for User Story 2

- [X] T020 [P] [US2] Implement Chainlink Proof of Reserve / NAVLink verification service for tokenized RWAs in `backend/src/services/rwa_verifier.py`
- [X] T021 [US2] Implement manual deal CRUD endpoints `GET` and `POST /api/v1/blotter/{wallet_address}/deals` in `backend/src/api/blotter.py`
- [X] T022 [US2] Implement consolidated portfolio position blending service (combining on-chain holdings and manual blotter deals) in `backend/src/services/portfolio_aggregator.py`
- [X] T023 [P] [US2] Implement manual deal entry modal form with field-level validation (Crypto, RWA, Perps) in `frontend/src/components/blotter/DealEntryModal.tsx`
- [X] T024 [US2] Implement trade blotter view with filtering across asset classes in `frontend/src/components/blotter/BlotterTable.tsx`
- [X] T025 [US2] Implement dedicated blotter management page in `frontend/src/app/blotter/page.tsx`

**Checkpoint**: User Stories 1 AND 2 both work independently and integrate seamlessly.

---

## Phase 5: User Story 3 - Single-Position Quantitative Risk Analytics (Priority: P2)

**Goal**: Calculate and display quantitative sensitivity and performance metrics for each position: Beta (BTC reference index), Delta, Volatility, Standard Deviation, Sharpe ratio ($R_f=0$), and Treynor ratio ($R_f=0$).

**Independent Test**: Select any position in the blotter or holdings table; verify that the single-deal risk drawer displays Beta (benchmarked against BTC), Delta, Volatility, StdDev, Sharpe, and Treynor ratios computed over the historical window.

### Implementation for User Story 3

- [X] T026 [P] [US3] Implement historical price series retrieval and daily log-return calculations in `backend/src/math/returns.py`
- [X] T027 [P] [US3] Implement Beta calculation benchmarked against Bitcoin ($BTC$) reference index in `backend/src/math/beta.py`
- [X] T028 [P] [US3] Implement position Delta, period Volatility, and Standard Deviation in `backend/src/math/volatility.py`
- [X] T029 [P] [US3] Implement single-asset Sharpe and Treynor ratios assuming $R_f = 0$ in `backend/src/math/ratios.py`
- [X] T030 [US3] Implement single-deal risk calculation endpoint `POST /api/v1/risk/single` in `backend/src/api/risk.py`
- [X] T031 [P] [US3] Implement single-deal risk analytics drawer UI with formula explanations in `frontend/src/components/risk/SingleRiskDrawer.tsx`
- [X] T032 [US3] Connect single-position risk drawer to holdings and blotter rows in `frontend/src/components/dashboard/HoldingsTable.tsx`

**Checkpoint**: Individual risk factor attribution is complete and testable.

---

## Phase 6: User Story 4 - Portfolio-Level Greeks & Covariance Matrix (Priority: P2)

**Goal**: Aggregate whole-portfolio Net Delta, Net Vega, Net Gamma, compute symmetric $N \times N$ Variance-Covariance matrix, and display portfolio-wide Sharpe & Treynor ratios.

**Independent Test**: Load a multi-asset portfolio; verify that Net Delta, Net Vega, Net Gamma, and portfolio Sharpe/Treynor render in executive cards, and an interactive $N \times N$ Variance-Covariance matrix displays pairwise covariances and correlation color heatmaps.

### Implementation for User Story 4

- [X] T033 [P] [US4] Implement Black-Scholes and synthetic derivative Greek sensitivities (Delta, Gamma, Vega) in `backend/src/math/greeks.py`
- [X] T034 [P] [US4] Implement high-dimensional $N \times N$ variance-covariance matrix and correlation calculations with Redis caching in `backend/src/math/covariance.py`
- [X] T035 [US4] Implement portfolio-level Greek aggregation and portfolio Sharpe & Treynor in `backend/src/math/portfolio_risk.py`
- [X] T036 [US4] Implement portfolio risk analytics endpoint `POST /api/v1/risk/portfolio` in `backend/src/api/risk.py`
- [X] T037 [P] [US4] Implement executive Net Greeks summary cards (Net Delta, Net Vega, Net Gamma) in `frontend/src/components/dashboard/NetGreeksCards.tsx`
- [X] T038 [P] [US4] Implement interactive heat-mapped $N \times N$ Variance-Covariance matrix component in `frontend/src/components/risk/CovarianceMatrix.tsx`
- [X] T039 [US4] Implement correlation and portfolio risk analytics page in `frontend/src/app/correlation/page.tsx`

**Checkpoint**: Portfolio Greek sensitivities and asset correlation matrix are fully functional.

---

## Phase 7: User Story 5 - Tail-Risk Report & Consent-Gated Rebalancing (Priority: P3)

**Goal**: Generate 95% and 99% Value at Risk (VaR) and Expected Shortfall (CVaR) reports, formulate risk-reduction rebalance proposals, fetch read-only 1inch Fusion / Uniswap quotes, and interact with a Gemini-powered grounded copilot.

**Independent Test**: Click "Generate Risk Report" to inspect 1-day 95%/99% VaR and Expected Shortfall; review suggested rebalancing trades; fetch 1inch/Uniswap quote; verify that execution requires explicit user wallet confirmation and transaction signing; test Gemini copilot chat explaining risk numbers.

### Implementation for User Story 5

- [X] T040 [P] [US5] Implement Parametric and Historical Value at Risk (VaR 95%/99%) and Expected Shortfall (CVaR 95%/99%) in `backend/src/math/tail_risk.py`
- [X] T041 [P] [US5] Implement rebalance advisor generating risk-reduction trade proposals in `backend/src/math/rebalance_advisor.py`
- [X] T042 [P] [US5] Implement read-only quote fetcher for 1inch Fusion and Uniswap in `backend/src/services/swaps.py`
- [X] T043 [US5] Implement risk report generation and rebalance quote endpoints in `backend/src/api/risk.py` and `backend/src/api/rebalance.py`
- [X] T044 [P] [US5] Implement Google GenAI Gemini copilot service with tool calling grounded in portfolio data in `backend/src/services/gemini.py`
- [X] T045 [US5] Implement copilot chat streaming endpoint `POST /api/v1/copilot/chat` in `backend/src/api/copilot.py`
- [X] T046 [P] [US5] Implement Risk Report generator and tail-risk distribution chart in `frontend/src/components/reports/RiskReportView.tsx`
- [X] T047 [P] [US5] Implement rebalancing proposal modal with pre-flight simulation and wallet signature prompt in `frontend/src/components/rebalance/RebalanceModal.tsx`
- [X] T048 [P] [US5] Implement Gemini chat copilot drawer UI with function calling transparency in `frontend/src/components/copilot/CopilotDrawer.tsx`
- [X] T049 [US5] Implement risk reports and rebalancing advisor page in `frontend/src/app/reports/page.tsx`

**Checkpoint**: End-to-end risk reporting, consensual rebalancing advisor, and AI copilot are fully functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Analytical test suites, graceful degradation indicators, and quickstart validation

- [X] T050 [P] Implement automated unit tests for math routines (Beta, Greeks, Covariance, VaR, CVaR) in `backend/tests/unit/test_math.py`
- [X] T051 [P] Implement integration tests for portfolio sync and rebalance quotes in `backend/tests/integration/test_portfolio_sync.py`
- [X] T052 Implement graceful degradation alerts and data provenance indicators across frontend views in `frontend/src/components/layout/ProvenanceAlert.tsx`
- [X] T053 Execute end-to-end validation scenarios per `specs/001-agentic-risk-manager/quickstart.md`
- [X] T054 [P] Finalize setup instructions and deployment documentation in `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3–7)**:
  - **User Story 1 (P1)**: Starts after Phase 2 (MVP)
  - **User Story 2 (P1)**: Starts after Phase 2 (blends with US1 holdings)
  - **User Story 3 (P2)**: Starts after Phase 2 (uses positions from US1/US2)
  - **User Story 4 (P2)**: Starts after Phase 2 (uses returns from US3)
  - **User Story 5 (P3)**: Starts after Phase 2 (requires metrics from US4)
- **Polish (Phase 8)**: Runs after all desired user stories are implemented

### Parallel Opportunities

- **Phase 1**: T002, T003, and T004 can run in parallel
- **Phase 2**: T006, T007, T008, T009, T011, and T012 can run in parallel
- **Phase 3 (US1)**: Backend services (T013, T014) and frontend header (T017) can run in parallel
- **Phase 4 (US2)**: Verifier (T020) and entry modal (T023) can run in parallel
- **Phase 5 (US3)**: All math routines (T026, T027, T028, T029) and UI drawer (T031) can run in parallel
- **Phase 6 (US4)**: Greeks math (T033), covariance math (T034), cards (T037), and matrix UI (T038) can run in parallel
- **Phase 7 (US5)**: Tail risk math (T040), rebalance math (T041), swap service (T042), Gemini service (T044), and UI modals (T046, T047, T048) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T012)
3. Complete Phase 3: User Story 1 (T013–T019)
4. **STOP and VALIDATE**: Verify wallet connection, ENS resolution, and multi-chain balance discovery.

### Incremental Delivery
1. Foundation + US1 → Live MVP with on-chain holdings discovery.
2. Add US2 → Trade blotter supporting manual entries (RWAs, CEX, Perps).
3. Add US3 → Single-position risk diagnostics (Beta vs BTC, Volatility, Sharpe, Treynor).
4. Add US4 → Portfolio Net Greeks and interactive Covariance Matrix.
5. Add US5 → VaR / Expected Shortfall reports, consensual 1inch/Uniswap rebalancing, and Gemini Copilot.
