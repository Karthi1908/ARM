import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Numeric, Integer, Boolean, DateTime, Date, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.src.core.database import Base

class WalletSession(Base):
    __tablename__ = "wallet_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    address = Column(String(42), nullable=False, index=True, unique=True)
    ens_name = Column(String(255), nullable=True)
    auth_provider = Column(String(50), nullable=False, default="privy")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(64), primary_key=True)  # e.g., "ETH", "BTC", "USDC", "ONDO_USDY"
    symbol = Column(String(32), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    asset_class = Column(String(32), nullable=False)  # "crypto", "rwa", "perpetual"
    decimals = Column(Integer, default=18)
    is_benchmark = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Position(Base):
    __tablename__ = "positions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_address = Column(String(42), nullable=False, index=True)
    asset_id = Column(String(64), ForeignKey("assets.id"), nullable=False)
    source_type = Column(String(32), nullable=False)  # "on_chain_discovered", "manual_entry"
    chain_id = Column(Integer, nullable=True)
    quantity = Column(Numeric(38, 18), nullable=False, default=0)
    unit_price_usd = Column(Numeric(24, 8), nullable=False, default=0)
    total_value_usd = Column(Numeric(24, 2), nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ManualDeal(Base):
    __tablename__ = "manual_deals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_address = Column(String(42), nullable=False, index=True)
    asset_name = Column(String(64), nullable=False)
    trade_date = Column(Date, nullable=False, default=date.today)
    side = Column(String(8), nullable=False)  # "buy", "sell"
    trade_type = Column(String(32), nullable=False)  # "spot", "forward", "future", "option_call", "option_put"
    asset_class = Column(String(32), nullable=False)  # "crypto", "rwa", "perpetual"
    settlement_date = Column(Date, nullable=True)
    venue = Column(String(64), nullable=False)
    quantity = Column(Numeric(38, 18), nullable=False)
    cost_basis_usd = Column(Numeric(24, 8), nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    time = Column(DateTime, nullable=False, index=True)
    asset_id = Column(String(64), ForeignKey("assets.id"), nullable=False, index=True)
    price_usd = Column(Numeric(24, 8), nullable=False)
    return_daily = Column(Numeric(12, 6), nullable=True)
    source = Column(String(32), nullable=False)  # "chainlink", "coingecko", "defillama", "navlink"


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_address = Column(String(42), nullable=False, index=True)
    net_delta = Column(Numeric(18, 4), nullable=False)
    net_gamma = Column(Numeric(18, 6), nullable=False)
    net_vega = Column(Numeric(18, 4), nullable=False)
    var_95_usd = Column(Numeric(24, 2), nullable=False)
    var_99_usd = Column(Numeric(24, 2), nullable=False)
    es_95_usd = Column(Numeric(24, 2), nullable=False)
    es_99_usd = Column(Numeric(24, 2), nullable=False)
    sharpe_ratio = Column(Numeric(8, 4), nullable=False)
    treynor_ratio = Column(Numeric(8, 4), nullable=False)
    matrix_snapshot = Column(JSON, nullable=False)
    math_engine_version = Column(String(32), nullable=True, default="v1.1.0")
    created_at = Column(DateTime, default=datetime.utcnow)


class RebalanceProposal(Base):
    __tablename__ = "rebalance_proposals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("risk_reports.id"), nullable=True)
    wallet_address = Column(String(42), nullable=False, index=True)
    status = Column(String(24), nullable=False, default="proposed")
    actions_json = Column(JSON, nullable=False)
    quote_details = Column(JSON, nullable=True)
    risk_delta_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
