<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- List of modified principles:
  - I. Non-Custodial by Default: Expanded with Privy, World ID, and The Graph/subgraphs integration requirements.
  - II. Read-First, Execute-Only-on-Explicit-Consent: Clarified explicit user consent requirement for rebalance routes (e.g., 1inch, Uniswap).
  - III. Deterministic, Versioned Risk Math: Reaffirmed versioned math contracts across all individual deal and portfolio metrics.
  - IV. Data Provenance & Graceful Degradation: Explicitly incorporated Chainlink oracles, CEX feeds, and DEX pool data provenance.
  - V. Chain- and Venue-Agnostic Core with Pluggable Adapters: Added hackathon EVM execution scope constraint while preserving agnostic core.
  - VI. Observability, Explainability & Auditability: Emphasized auditability of rebalancing suggestions and risk reports.
  - VII. Progressive Disclosure UX: Refined UX hierarchy for risk metrics and reports.
- Added sections: None
- Removed sections: None
- Follow-up TODOs: None
-->

# Crypto Risk Manager Constitution

## Core Principles

### I. Non-Custodial by Default
The system MUST NEVER request, store, or custody private keys, seed phrases, or credentials. User identity and authentication MUST rely on non-custodial authentication and identity providers (such as Privy and World ID) alongside standard injected/EIP-1193 wallets. Portfolio position discovery and on-chain token balance fetching MUST operate via decentralized indexing networks (such as The Graph and protocol subgraphs) and public RPCs without requiring transaction signing permissions.

### II. Read-First, Execute-Only-on-Explicit-Consent
All automated scanning, balance discovery, and risk monitoring pipelines MUST operate strictly in read-only mode. Even when the engine generates portfolio rebalancing recommendations, autonomous trade execution is strictly forbidden. Any trade routing or execution (e.g., via 1inch, Uniswap, or other DEX aggregators) MUST require unambiguous, explicit user confirmation and interactive wallet signature verification.

### III. Deterministic, Versioned Risk Math
All mathematical models—including single-deal metrics (Beta vs. Bitcoin reference index, Delta, Volatility, Standard Deviation, Sharpe ratio with $R_f = 0$, Treynor ratio with $R_f = 0$) and portfolio-level aggregates (Net Delta, Net Vega, Net Gamma, Variance-Covariance matrix, Value at Risk [VaR], and Expected Shortfall [CVaR])—MUST be deterministic, unit-tested, and version-tagged. All risk engines MUST explicitly document calculation windows, underlying confidence intervals, and reference index parameters.

### IV. Data Provenance & Graceful Degradation
Every market price, index feed, on-chain balance, and historical time series—whether derived from decentralized oracles (e.g., Chainlink), centralized exchanges (CEX APIs), or decentralized pools (DEX subgraphs)—MUST record its source provenance, latency, and timestamp metadata. If an external oracle, API, or RPC node fails or is rate-limited, the system MUST gracefully degrade to cached states with explicit staleness and confidence warnings, never failing silently or presenting unverified data.

### V. Chain- and Venue-Agnostic Core with Pluggable Adapters (Hackathon Scope: EVM)
The core domain model for assets, positions, and trades (covering Spot Crypto, Real World Assets [RWAs], and Perpetual/Derivative contracts) MUST remain decoupled from specific chains, decentralized protocols, and centralized exchanges. External data ingestion and execution MUST be implemented through standardized, pluggable adapter interfaces. For hackathon delivery, transaction execution adapters and protocol connectors are scoped to EVM-compatible networks while preserving the multi-chain domain core.

### VI. Observability, Explainability & Auditability
Every generated risk metric, risk report, and portfolio rebalancing suggestion MUST be fully observable, explainable, and auditable. The system MUST expose intermediate calculation steps, baseline assumptions, historical lookback horizons, and weighting mechanisms behind every suggested rebalancing action.

### VII. Progressive Disclosure UX
The user interface MUST present complex financial risk insights through progressive disclosure: surface high-level summary health indicators, net Greek exposures (Delta, Gamma, Vega), and portfolio VaR/ES immediately, while providing intuitive drill-down into position-level parameters (Beta, Sharpe, Treynor), deal entry logs, variance-covariance matrices, and actionable rebalancing diagnostics.

## Mathematical & Risk Modeling Standards

1. **Benchmark Standard**: Bitcoin (BTC) is established as the default reference index for systematic risk and Beta estimations across all crypto and crypto-derivative assets unless explicitly configured otherwise.
2. **Baseline Assumptions**: Risk-free rate ($R_f$) defaults to 0% for base Sharpe and Treynor ratio calculations, reflecting crypto-native baseline benchmarks.
3. **Multi-Asset Coverage**: The risk core MUST natively support Spot Crypto, Perpetual/Derivative contracts (capturing Greeks: Delta, Gamma, Vega), and Tokenized Real World Assets (RWAs) with settlement date and trade venue attributes.
4. **Tail Risk Metrics**: Portfolio risk reports MUST compute parametric and historical Value at Risk (VaR) alongside Expected Shortfall (Conditional VaR) at standardized confidence intervals (e.g., 95% and 99%).

## Development Workflow & Quality Gates

1. **Test-Driven Math Verification**: Every financial math formula and risk calculation routine MUST have comprehensive unit tests verifying analytical correctness against verified reference benchmarks before merging.
2. **Adapter Isolation**: Adapters for specific blockchains or exchange APIs MUST be verified with isolated mock fixtures and integration tests to ensure network faults do not compromise the core risk engine.
3. **Zero Secrets Leakage**: Continuous integration (CI) MUST enforce automated secret scanning to prevent API keys or sensitive credentials from entering codebase repositories.
4. **Documentation Sync**: Any revision to risk metrics, mathematical formulas, or default assumptions MUST trigger a corresponding update in system architecture and user documentation.

## Governance

This Constitution serves as the definitive authority on architectural, mathematical, and security standards for the Crypto Risk Manager. All pull requests, feature specifications, and implementation plans MUST strictly comply with these principles.

- **Amendments**: Amendments require documented rationale, impact assessments on risk computations, and a formal version bump.
- **Versioning Policy**:
  - **MAJOR** version bumps for breaking shifts in non-custodial boundaries, math conventions, or core governance.
  - **MINOR** version bumps for added principles, new asset classes, or expanded modeling standards.
  - **PATCH** version bumps for clarifications, typo fixes, and non-semantic documentation refinements.
- **Compliance**: Continuous integration gates and code reviews MUST verify that new implementations adhere to non-custodial constraints, deterministic math guarantees, and data provenance requirements.

**Version**: 1.1.0 | **Ratified**: 2026-09-06 | **Last Amended**: 2026-09-07
