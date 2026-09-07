from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Authentication & Session Schemas ---
class WalletSessionCreate(BaseModel):
    address: str = Field(..., example="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
    auth_provider: str = Field("privy", example="privy")

class WalletSessionResponse(BaseModel):
    address: str
    ens_name: Optional[str] = None
    auth_provider: str
    created_at: Optional[datetime] = None


# --- Position & Portfolio Schemas ---
class PositionResponse(BaseModel):
    id: str
    asset_id: str
    symbol: str
    name: str
    asset_class: str  # "crypto", "rwa", "perpetual"
    source_type: str  # "on_chain_discovered", "manual_entry"
    chain_id: Optional[int] = None
    quantity: float
    unit_price_usd: float
    total_value_usd: float

class PortfolioResponse(BaseModel):
    wallet_address: str
    total_value_usd: float
    positions: List[PositionResponse]

class PortfolioSyncResponse(BaseModel):
    discovered_count: int
    chains_scanned: List[int]
    synced_at: datetime


# --- Manual Deal Schemas ---
class ManualDealCreate(BaseModel):
    asset_name: str
    trade_date: date
    side: str = Field(..., pattern="^(buy|sell)$")
    trade_type: str = Field("spot", pattern="^(spot|forward|future|option_call|option_put)$")
    asset_class: str = Field(..., pattern="^(crypto|rwa|perpetual)$")
    settlement_date: Optional[date] = None
    venue: str
    quantity: float = Field(..., gt=0)
    cost_basis_usd: float = Field(..., gt=0)
    notes: Optional[str] = None

class ManualDealResponse(BaseModel):
    id: str
    wallet_address: str
    asset_name: str
    trade_date: date
    side: str
    trade_type: str
    asset_class: str
    settlement_date: Optional[date]
    venue: str
    quantity: float
    cost_basis_usd: float
    notes: Optional[str]
    created_at: datetime


# --- Quantitative Risk Schemas ---
class SingleRiskRequest(BaseModel):
    asset_id: str
    lookback_days: int = 90

class SingleRiskResponse(BaseModel):
    asset_id: str
    reference_index: str = "BTC"
    beta: float
    delta: float
    volatility_annualized: float
    standard_deviation: float
    sharpe_ratio: float
    treynor_ratio: float
    historical_points_used: int

class PortfolioRiskRequest(BaseModel):
    wallet_address: str
    lookback_days: int = 90

class PortfolioRiskResponse(BaseModel):
    wallet_address: str
    net_delta: float
    net_gamma: float
    net_vega: float
    sharpe_ratio: float
    treynor_ratio: float
    assets: List[str]
    covariance_matrix: List[List[float]]
    correlation_matrix: List[List[float]]

class RebalanceAction(BaseModel):
    action_type: str  # "trim", "accumulate", "hedge"
    asset_id: str
    target_delta_usd: float
    rationale: str
    recommended_venue: str  # "1inch", "uniswap"

class RiskReportRequest(BaseModel):
    wallet_address: str
    confidence_levels: List[float] = [0.95, 0.99]

class RiskReportResponse(BaseModel):
    report_id: str
    timestamp: datetime
    var_95_usd: float
    var_99_usd: float
    es_95_usd: float
    es_99_usd: float
    rebalancing_suggestions: List[RebalanceAction]


# --- Rebalance Quote Schemas ---
class RebalanceQuoteRequest(BaseModel):
    chain_id: int
    from_token: str
    to_token: str
    amount: str
    venue: str = "1inch"  # "1inch", "uniswap"

class RebalanceQuoteResponse(BaseModel):
    venue: str
    from_amount: str
    to_amount: str
    estimated_slippage_bps: int
    gas_estimate_usd: float
    unsigned_tx: Dict[str, Any]


# --- Gemini Copilot Schemas ---
class CopilotChatRequest(BaseModel):
    wallet_address: str
    message: str
    conversation_id: Optional[str] = None

class CopilotChatResponse(BaseModel):
    response_text: str
    tool_calls_executed: List[str] = []
    proposed_rebalance: Optional[Dict[str, Any]] = None
