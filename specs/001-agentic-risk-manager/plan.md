# Implementation Plan: Uniswap AI Hedging Agent (Positions to USDC / ETH)

**Branch**: `001-agentic-risk-manager` | **Spec**: [spec.md](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/specs/001-agentic-risk-manager/spec.md) | **Date**: 2026-09-09

## Summary

Implement a conversational and interactive **Uniswap AI Hedging Agent** that enables users to hedge or close open crypto and derivative positions into **USDC** or **ETH** (and vice versa). The agent prompts the user for the specific **token** and **quantity** (or percentage of holding), computes optimal swap routing and pre-flight parameters using Uniswap AI skills/routing, and generates an un-signed transaction payload for the user's explicit 1-click wallet confirmation and signing.

---

## Technical Context

**Primary Frameworks**:
- Backend: Python 3.11+ / FastAPI, `google-genai` (Gemini SDK), `httpx`
- Frontend: Next.js 14.2.5 (App Router), TypeScript, `@privy-io/react-auth`, `viem`

**External Integrations**:
- Uniswap AI skill framework (`https://github.com/Uniswap/uniswap-ai`)
- Uniswap Routing & V3/V4 Quoting API
- Non-custodial wallet execution (Privy / EIP-1193)

---

## Constitution Check

| Principle | Check / Gate | Status | Notes |
| :--- | :--- | :--- | :--- |
| **I. Non-Custodial by Default** | System never touches private keys | **PASS** | Agent only generates un-signed transaction payloads; keys remain in user wallets. |
| **II. Read-First, Consent-Only** | Trades require explicit user confirmation and signature | **PASS** | Agent proposes and routes; user must confirm and sign via modal. |
| **III. Deterministic Risk Math** | Math models remain reproducible | **PASS** | Token valuations and slippage estimations are calculated with deterministic fee tiers. |
| **IV. Data Provenance & Degradation** | Market routes provide provenance | **PASS** | Pool paths and quotes display source venue (`Uniswap AI Route`). |
| **V. Pluggable Adapters (EVM)** | Uniswap EVM routing adapter | **PASS** | Implemented as decoupled `UniswapAIAgentService` adapter. |

---

## Proposed Changes

### 1. Backend Core & Services

#### [NEW] [`backend/src/services/uniswap_ai.py`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/backend/src/services/uniswap_ai.py)
- Implements `UniswapAIAgentService` incorporating the Uniswap AI routing skill patterns.
- Functions:
  - `parse_hedge_intent(user_message, current_positions)`: Extracts source token, target token (`USDC` or `ETH`), and quantity/percentage from natural language or structured requests. If incomplete, prompts the user for the missing parameter (e.g., *"Which token would you like to hedge, and what quantity?"*).
  - `get_hedge_quote(chain_id, from_token, to_token, amount, wallet_address)`: Obtains optimized Uniswap pool routing (V3/V4/UniswapX), estimated execution price, price impact, slippage, and un-signed transaction payload (`to`, `data`, `value`, `estimatedGas`).

#### [MODIFY] [`backend/src/services/gemini.py`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/backend/src/services/gemini.py)
- Register `uniswap_hedge_advisor` tool in `gemini_copilot`.
- Ground the Copilot system prompt with instructions:
  - When the user asks to hedge or close positions, actively inquire: *"Which token and what quantity would you like to convert into USDC or ETH?"*
  - When token and quantity are provided, call `uniswap_ai.get_hedge_quote()` and package a structured `proposed_rebalance` payload with pre-flight metrics.

#### [MODIFY] [`backend/src/models/schemas.py`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/backend/src/models/schemas.py)
- Extend `CopilotChatResponse` and `RebalanceQuoteResponse` to support Uniswap AI routing metadata:
  - `target_hedge_asset`: `"USDC"` | `"ETH"`
  - `swap_route_summary`: String description of Uniswap pool route.
  - `price_impact_bps`: Estimated price impact in basis points.

#### [MODIFY] [`backend/src/api/rebalance.py`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/backend/src/api/rebalance.py)
- Update `POST /api/v1/rebalance/quote` to route through `UniswapAIAgentService` when `venue="uniswap"`, returning full calldata and pre-flight simulation metrics.

---

### 2. Frontend User Experience

#### [MODIFY] [`frontend/src/components/copilot/CopilotDrawer.tsx`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/frontend/src/components/copilot/CopilotDrawer.tsx)
- Add direct UI interaction cards when the Copilot suggests or asks for a hedge:
  - Interactive **Quick Tokens** buttons (e.g., `[Convert 50% ETH to USDC]`, `[Convert 100% SOL to USDC]`, `[Convert USDC to ETH]`).
  - Render an interactive **"Review & Sign Uniswap Hedge"** button in message bubbles containing `rebalanceProposal`.
  - Clicking launches the pre-flight `RebalanceModal` populated with the exact parameters from the chat.

#### [MODIFY] [`frontend/src/components/rebalance/RebalanceModal.tsx`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/frontend/src/components/rebalance/RebalanceModal.tsx)
- Support selecting `USDC` or `ETH` as target hedge currencies.
- Display Uniswap AI routing badge (`Uniswap AI Route`), pool fee tiers, and price impact.
- Provide a clean 1-click button: **"Sign in Wallet to Execute Swap"** which triggers client-side EIP-1193 / Privy transaction signing.

#### [MODIFY] [`frontend/src/components/dashboard/HoldingsTable.tsx`](file:///c:/Users/Karth/hacks-projects/agentic_risk_manager/frontend/src/components/dashboard/HoldingsTable.tsx)
- Add a quick action button in each position row: **"Hedge into USDC"** that pre-fills the Copilot or opens the Hedge Modal directly for that asset.

---

## Verification Plan

### Automated Tests
- `pytest backend/tests/unit/test_uniswap_ai.py`:
  - Unit tests verifying natural language parsing of hedge requests (`"hedge 2.5 ETH to USDC"`, `"close my SOL to ETH"`, `"convert 50% of my OP"`).
  - Validation of fallback prompt when token or quantity is missing.
  - Verification of un-signed transaction payload structure and non-custodial guardrails.
- `pytest backend/tests/integration/test_rebalance_quote.py`:
  - Verification of `POST /api/v1/rebalance/quote` with `venue="uniswap"`.

### Manual End-to-End Verification
1. Launch app with connected wallet holding assets.
2. Open **AI Risk Copilot** and type: *"I want to hedge my position"*.
3. Verify Copilot asks for the **token** and **quantity** to convert into **USDC** or **ETH**.
4. Reply: *"Convert 1.5 ETH into USDC"*.
5. Verify Copilot displays the Uniswap quote with pool details and an action card: **"Review Uniswap Hedge"**.
6. Click the card to open `RebalanceModal`, inspect slippage, and click **"Sign in Wallet to Execute"**.
7. Confirm simulated / real wallet signature verification succeeds.
