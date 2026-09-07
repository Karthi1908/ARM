# Feature Specification: Agentic Crypto Risk Manager

**Feature Branch**: `001-agentic-risk-manager`

**Created**: 2026-09-07

**Status**: Draft

**Input**: User description: "Build a Agentic Risk Manager web application. Users log in by connecting a crypto wallet. Once connected, the app automatically fetches and displays all of the user's crypto holdings across multiple blockchains for that wallet, valued in USD. Users can also manually add positions the wallet won't show automatically — for example trades made on a centralized exchange, OTC deals, tokenized real-world assets, or perpetual futures. Each manual position needs: the crypto/asset name, trade date, side (buy or sell), type of trade, asset class (crypto, real-world asset, or perpetual), settlement date, and the exchange or venue where the trade happened. For any single position — whether discovered on-chain or entered manually — the app should show: beta (using Bitcoin as the reference index), delta, volatility, standard deviation, Sharpe ratio, and Treynor ratio. Assume a risk-free rate of 0. At the whole-portfolio level, the app should show: net delta, net vega, net gamma, the variance-covariance matrix of the held assets, and portfolio-level Sharpe ratio and Treynor ratio (also assuming a 0% risk-free rate). Finally, users should be able to generate a risk report that calculates Value at Risk (VaR) and Expected Shortfall, and gives suggestions for rebalancing the portfolio to reduce risk. The app should never execute a trade on the user's behalf — any suggested rebalancing action requires the user to confirm and sign it themselves in their own wallet."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Chain Wallet Discovery & Unified Holdings (Priority: P1)

As a crypto investor holding assets across multiple networks, I want to connect my wallet and immediately view my consolidated crypto holdings across multiple blockchains with their current USD valuations, so that I have complete visibility into my liquid on-chain portfolio without manual tracking.

**Why this priority**: Core value entry point; without asset discovery and valuation, no risk calculations can be executed.

**Independent Test**: Can be fully tested by connecting an EVM wallet with existing balances across multiple networks (e.g., Ethereum Mainnet, Arbitrum, Optimism, Base). The system successfully discovers tokens, looks up USD prices, and displays the unified on-chain portfolio balance table.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user, **When** they initiate a wallet connection and approve the session, **Then** the system establishes a non-custodial session and displays their public wallet address.
2. **Given** a connected wallet with token holdings across multiple supported blockchains, **When** the portfolio dashboard loads, **Then** the application automatically fetches and lists each token, its chain of origin, held quantity, current market price in USD, and total USD position value.
3. **Given** a connected wallet with no holdings on a specific supported chain, **When** discovery completes, **Then** the application displays an empty balance state for that chain without crashing or blocking other chains.

---

### User Story 2 - Multi-Asset Manual Deal Blotter (Priority: P1)

As an active trader with positions outside of standard on-chain wallet tokens (such as CEX trades, OTC contracts, Tokenized Real-World Assets [RWAs], and Perpetual futures), I want to manually record these positions with complete deal attributes, so that my entire multi-asset book is modeled in one unified risk platform.

**Why this priority**: Complete risk management requires accounting for off-chain, OTC, derivative, and RWA positions alongside liquid wallet balances.

**Independent Test**: Can be fully tested by entering a manual position (specifying asset name, trade date, buy/sell side, trade type, asset class, settlement date, and venue). The position is validated, stored, valued in USD, and reflected in the consolidated portfolio blotter.

**Acceptance Scenarios**:

1. **Given** a user on the Deal Blotter interface, **When** they fill out a manual position form specifying asset name, trade date, side (Buy/Sell), trade type, asset class (Crypto, Real-World Asset, or Perpetual), settlement date, and exchange/venue, **Then** the deal is saved and displayed in the consolidated positions blotter.
2. **Given** an existing manual deal entry, **When** the user edits or deletes the deal, **Then** the portfolio blotter and aggregate USD exposure instantly recalculate.
3. **Given** invalid or incomplete inputs (e.g., missing settlement date for an RWA or negative position quantity), **When** the user attempts to submit, **Then** the form blocks submission with field-level validation errors.

---

### User Story 3 - Single-Position Quantitative Risk Analytics (Priority: P2)

As a risk-conscious trader, I want to inspect quantitative sensitivity and performance metrics for any individual holding—whether discovered on-chain or entered manually—so that I understand its systematic risk, volatility, and risk-adjusted efficiency.

**Why this priority**: Enables users to identify outsized risks, high volatility, and poorly performing positions at the unit level.

**Independent Test**: Can be fully tested by selecting any active position and verifying that the risk card displays Beta (against BTC), Delta, Volatility, Standard Deviation, Sharpe Ratio ($R_f=0$), and Treynor Ratio ($R_f=0$) based on historical market data.

**Acceptance Scenarios**:

1. **Given** a position in the blotter (e.g., ETH spot or a perpetual position), **When** the user views its risk details, **Then** the system displays:
   - **Beta ($\beta$)**: benchmarked against Bitcoin ($BTC$) as the reference index.
   - **Delta ($\Delta$)**: directional price sensitivity.
   - **Volatility ($\sigma$)**: annualized volatility of returns.
   - **Standard Deviation**: dispersion of returns over the calculation window.
   - **Sharpe Ratio**: risk-adjusted return relative to total volatility ($R_f = 0$).
   - **Treynor Ratio**: risk-adjusted return relative to systematic Beta ($R_f = 0$).
2. **Given** an asset with an inverse or short position (e.g., short perpetual contract), **When** calculating risk metrics, **Then** the Delta and Beta correctly reflect negative directional exposure.

---

### User Story 4 - Portfolio-Level Greeks & Covariance Matrix (Priority: P2)

As a portfolio manager, I want to evaluate whole-portfolio risk through aggregate Greeks, asset-to-asset correlations, and portfolio-wide risk ratios, so that I can manage systemic exposure and diversification across all asset classes.

**Why this priority**: True risk management happens at the portfolio level; asset correlations and non-linear Greek exposures determine solvency and vulnerability to market shocks.

**Independent Test**: Can be fully tested with a multi-asset portfolio. The application computes and displays Net Delta, Net Vega, Net Gamma, the complete symmetric $N \times N$ Variance-Covariance matrix, Portfolio Sharpe Ratio ($R_f = 0$), and Portfolio Treynor Ratio ($R_f = 0$).

**Acceptance Scenarios**:

1. **Given** a portfolio with multiple positions across Spot, RWAs, and Derivatives, **When** viewing the Portfolio Risk dashboard, **Then** the system displays Net Delta, Net Vega, and Net Gamma aggregated across all holdings.
2. **Given** $N$ active assets in the portfolio, **When** navigating to the Covariance view, **Then** an interactive $N \times N$ Variance-Covariance matrix is rendered with pairwise covariance values and correlation color gradients.
3. **Given** the overall portfolio returns time series, **When** the dashboard renders, **Then** the Portfolio Sharpe Ratio and Portfolio Treynor Ratio are computed and displayed assuming $R_f = 0$.

---

### User Story 5 - Tail-Risk Report & Consent-Gated Rebalancing (Priority: P3)

As a portfolio manager seeking downside protection, I want to generate a formal risk report providing Value at Risk (VaR) and Expected Shortfall (CVaR) alongside risk-mitigating rebalancing suggestions, which I can execute only through my own explicit wallet signature, so that my portfolio remains protected without relinquishing custody.

**Why this priority**: Delivers institutional risk assessment and actionable rebalancing while strictly honoring the non-custodial, consent-only constitutional mandate.

**Independent Test**: Can be fully tested by clicking "Generate Risk Report". The system computes parametric and historical VaR and Expected Shortfall at 95% and 99% confidence levels, produces concrete trade suggestions to reduce risk, and generates a pre-flight execution preview requiring the user's explicit interactive signature in their wallet.

**Acceptance Scenarios**:

1. **Given** an active portfolio, **When** the user clicks "Generate Risk Report", **Then** the application generates a report containing Value at Risk (VaR) and Expected Shortfall (Conditional VaR / ES) at 95% and 99% confidence intervals.
2. **Given** a portfolio with concentrated risk or high negative tail exposure, **When** the risk report is generated, **Then** the system provides actionable rebalancing suggestions (e.g., trim high-volatility assets, hedge net delta, reallocate to lower-beta assets).
3. **Given** suggested rebalancing actions, **When** the user chooses to proceed with a rebalancing recommendation, **Then** the system presents a detailed pre-flight simulation (assets involved, expected risk reduction, slippage/fees) and requires the user to confirm and sign the transaction in their connected wallet.
4. **Given** a rebalancing proposal, **When** the user dismisses the suggestion or rejects the wallet prompt, **Then** no transaction is broadcast and portfolio state remains unchanged.

---

### Edge Cases

- **RPC or Data Indexer Timeout**: If on-chain balance discovery or historical price indexing is delayed or unavailable for a specific chain or token, the system displays a graceful degradation warning with timestamped cached data rather than halting the entire dashboard.
- **Illiquid or New Token Without Historical Data**: If an asset lacks sufficient historical price data for a 90-day covariance or beta calculation, the system flags the asset with an "Insufficient History" indicator and excludes it from the beta matrix while including its known USD spot value in the portfolio total.
- **Single-Asset Portfolio**: If a portfolio contains only one asset, the variance-covariance matrix collapses to a single scalar variance, and the system prompts the user that portfolio diversification metrics require at least two distinct assets.
- **Zero Beta or Zero Volatility Asset**: If an asset (such as a pegged fiat stablecoin) exhibits zero volatility or zero beta, Sharpe and Treynor ratio calculations gracefully display "N/A (Zero Volatility / Zero Beta)" rather than returning division-by-zero errors.
- **Past Settlement Date**: If a manual RWA or forward contract settlement date is in the past, the system flags the position as "Matured / Settled" and provides options to archive or rollover.
- **Wallet Disconnection During Review**: If the user disconnects their wallet while viewing rebalancing suggestions, the execution interface disables itself immediately and prompts for reconnection.

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Asset Discovery
- **FR-001**: System MUST support non-custodial wallet connection using standard Web3 wallet protocols without requesting private keys or seed phrases.
- **FR-002**: System MUST automatically query and aggregate crypto token balances across multiple supported blockchain networks for the connected wallet address.
- **FR-003**: System MUST convert and display all discovered crypto balances in United States Dollars (USD) using current market price feeds.
- **FR-004**: System MUST display data provenance metadata, including price source and last updated timestamp, for all asset valuations.

#### Multi-Asset Deal Blotter
- **FR-005**: System MUST allow users to manually enter positions not discovered on-chain, including CEX trades, OTC contracts, Tokenized RWAs, and Perpetual futures.
- **FR-006**: Manual position entry MUST require: Asset Name/Symbol, Trade Date, Side (Buy or Sell), Trade Type, Asset Class (Crypto, Real-World Asset, or Perpetual), Settlement Date, and Execution Exchange/Venue.
- **FR-007**: System MUST validate all manual position fields, enforcing valid date formats and positive quantities.
- **FR-008**: System MUST allow users to view, update, and delete previously entered manual positions.
- **FR-009**: System MUST blend auto-discovered on-chain holdings and manually entered positions into a consolidated portfolio view.

#### Single-Position Risk Analytics
- **FR-010**: System MUST compute and display Beta ($\beta$) for each position using Bitcoin ($BTC$) as the standard reference market index.
- **FR-011**: System MUST compute and display Delta ($\Delta$) representing directional price sensitivity for each position.
- **FR-012**: System MUST compute and display historical Volatility ($\sigma$) and Standard Deviation for each position over a standard lookback window.
- **FR-013**: System MUST compute and display the Sharpe Ratio for each position assuming a risk-free rate of 0% ($R_f = 0$).
- **FR-014**: System MUST compute and display the Treynor Ratio for each position assuming a risk-free rate of 0% ($R_f = 0$).

#### Portfolio-Level Quantitative Risk Engine
- **FR-015**: System MUST aggregate and display Net Delta ($\Delta_{net}$) across all held positions.
- **FR-016**: System MUST aggregate and display Net Vega ($\nu_{net}$) across all derivative and perpetual holdings.
- **FR-017**: System MUST aggregate and display Net Gamma ($\Gamma_{net}$) across all derivative and perpetual holdings.
- **FR-018**: System MUST compute and render a symmetric $N \times N$ Variance-Covariance Matrix for all assets in the portfolio.
- **FR-019**: System MUST compute and display Portfolio Sharpe Ratio and Portfolio Treynor Ratio assuming a risk-free rate of 0% ($R_f = 0$).

#### Risk Reporting & Rebalancing Recommendations
- **FR-020**: System MUST provide an on-demand Risk Report generator calculating Value at Risk (VaR) at 95% and 99% confidence levels.
- **FR-021**: System MUST calculate Expected Shortfall (ES / Conditional VaR) at 95% and 99% confidence levels in the Risk Report.
- **FR-022**: System MUST provide actionable rebalancing suggestions designed to reduce portfolio concentration and downside tail risk.
- **FR-023**: System MUST explain the rationale behind each rebalancing suggestion, detailing the expected change in portfolio VaR, Net Greeks, and risk ratios.
- **FR-024**: System MUST NEVER autonomously execute trades, transactions, or balance shifts on behalf of the user.
- **FR-025**: Any rebalancing execution MUST require the user to review a pre-flight summary and interactively approve and sign the transaction in their connected wallet.

### Key Entities *(include if feature involves data)*

- **Wallet Session**: Represents an active non-custodial user session; attributes include public address, connected provider, and connection timestamp.
- **Position**: Represents an individual asset holding; attributes include asset symbol, asset class (Crypto, Real-World Asset, Perpetual), origin type (On-Chain Discovered or Manual Entry), quantity, unit price in USD, and total USD value.
- **Manual Deal**: Represents user-recorded off-chain or derivative trade details; attributes include deal ID, asset name, trade date, side (Buy/Sell), trade type, asset class, settlement date, venue/exchange, quantity, and cost basis.
- **Single-Deal Risk Profile**: Mathematical risk attributes for an individual position; attributes include Beta (vs. BTC), Delta, Volatility, Standard Deviation, Sharpe Ratio ($R_f=0$), and Treynor Ratio ($R_f=0$).
- **Portfolio Risk Profile**: Aggregated whole-portfolio risk attributes; attributes include Net Delta, Net Vega, Net Gamma, Portfolio Sharpe Ratio, Portfolio Treynor Ratio, and the $N \times N$ Variance-Covariance Matrix.
- **Risk Report**: Summary document of portfolio stress and tail risks; attributes include generation timestamp, 95% VaR, 99% VaR, 95% Expected Shortfall, 99% Expected Shortfall, asset concentration breakdown, and rebalancing recommendations.
- **Rebalancing Action**: Proposed trade adjustment; attributes include asset symbol, action type (Trim, Accumulate, Hedge), target quantity/notional, expected risk reduction impact, and pre-flight transaction payload.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can connect their wallet and view multi-chain token holdings consolidated in USD within 5 seconds under normal network conditions.
- **SC-002**: Users can complete a manual trade entry in under 30 seconds with immediate real-time updates to the consolidated portfolio blotter.
- **SC-003**: 100% of single-deal metrics (Beta vs. BTC, Delta, Volatility, Standard Deviation, Sharpe, Treynor) and portfolio Greeks are computed and displayed within 2 seconds of portfolio selection.
- **SC-004**: Variance-Covariance matrix renders accurately for up to 50 concurrent assets with color-coded correlation indicators.
- **SC-005**: Risk Report generation completes in under 3 seconds, delivering both 95% and 99% VaR and Expected Shortfall calculations.
- **SC-006**: 100% of suggested rebalancing actions require explicit user confirmation and wallet signature; zero autonomous trades are executed by the application.
- **SC-007**: 95% of users with diverse multi-asset holdings can navigate from portfolio overview to detailed risk report without encountering validation errors.
- **SC-008**: System achieves graceful degradation with visible staleness alerts when external price or data feeds experience latency exceeding 30 seconds.

## Assumptions

- **Reference Index**: Bitcoin ($BTC$) is the standardized reference benchmark for all systematic risk ($\beta$) and Treynor ratio calculations across crypto and crypto-derivative assets.
- **Risk-Free Rate**: A baseline risk-free rate of $R_f = 0\%$ is used across all Sharpe and Treynor ratio formulas, reflecting crypto-native conventions.
- **Historical Window**: Historical market data lookback window defaults to 90 days for return volatility, covariance, and beta estimations, with optional 180-day and 365-day views.
- **Tail-Risk Parameters**: Value at Risk (VaR) and Expected Shortfall calculations utilize standard 1-day holding periods evaluated at both 95% and 99% confidence horizons using parametric and historical methods.
- **Blockchain Scope**: Initial wallet discovery and rebalance execution routing target EVM-compatible networks in accordance with the project constitution hackathon scope.
- **Data Persistence**: Manual positions entered by the user are persisted in client-side secure local storage associated with the connected wallet address, maintaining privacy and non-custodial integrity.
- **Rebalancing Routing**: Rebalancing suggestions are routed through decentralized exchange protocols (such as Uniswap and 1inch), preparing executable transactions that require user signature in their personal wallet.
