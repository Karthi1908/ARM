import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.src.core.database import get_db
from backend.src.core.config import settings
from backend.src.models.entities import Position, Asset, RiskReport, ManualDeal
from backend.src.models.schemas import (
    SingleRiskRequest, SingleRiskResponse,
    PortfolioRiskRequest, PortfolioRiskResponse,
    RiskReportRequest, RiskReportResponse, RebalanceAction
)
from backend.src.services.oracles import oracle_service
from backend.src.services.indexer import indexer_service
from backend.src.math.returns import generate_historical_prices_and_returns
from backend.src.math.beta import calculate_beta
from backend.src.math.volatility import calculate_volatility_and_std, calculate_delta
from backend.src.math.ratios import calculate_sharpe_and_treynor
from backend.src.math.portfolio_risk import compute_portfolio_risk_profile
from backend.src.math.tail_risk import calculate_tail_risk
from backend.src.math.rebalance_advisor import generate_rebalance_suggestions

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/single", response_model=SingleRiskResponse)
async def get_single_risk_metrics(payload: SingleRiskRequest):
    raw_asset_id = payload.asset_id.upper()
    days = max(payload.lookback_days, settings.MIN_OBSERVATIONS_THRESHOLD)

    # Normalize compound IDs (e.g. ETH_1, ETH_MANUAL, USDC_1_0x...)
    symbol = raw_asset_id
    if symbol.endswith("_MANUAL"):
        symbol = symbol.replace("_MANUAL", "")
    elif "_" in symbol and not symbol.startswith(("TBILL_", "ONDO_")):
        parts = symbol.split("_")
        if len(parts) > 1 and (parts[1].isdigit() or parts[1].startswith("0X")):
            symbol = parts[0]

    price, _, _ = await oracle_service.get_price(symbol)
    btc_price, _, _ = await oracle_service.get_price("BTC")

    _, asset_returns = generate_historical_prices_and_returns(symbol, price, days=days)
    _, btc_returns = generate_historical_prices_and_returns("BTC", btc_price, days=days)

    beta = calculate_beta(asset_returns, btc_returns) if symbol != "BTC" else 1.0000
    delta = calculate_delta(side="buy", trade_type="spot")
    annualized_vol, daily_std = calculate_volatility_and_std(asset_returns)
    sharpe, treynor = calculate_sharpe_and_treynor(asset_returns, beta, risk_free_rate=settings.RISK_FREE_RATE)

    return SingleRiskResponse(
        asset_id=raw_asset_id,
        reference_index=settings.REFERENCE_BENCHMARK,
        beta=beta,
        delta=delta,
        volatility_annualized=annualized_vol,
        standard_deviation=daily_std,
        sharpe_ratio=sharpe,
        treynor_ratio=treynor,
        historical_points_used=len(asset_returns)
    )

@router.post("/portfolio", response_model=PortfolioRiskResponse)
async def get_portfolio_risk_metrics(
    payload: PortfolioRiskRequest,
    db: AsyncSession = Depends(get_db)
):
    addr_lower = payload.wallet_address.lower()

    stmt = select(Position).where(Position.wallet_address == addr_lower)
    result = await db.execute(stmt)
    positions = result.scalars().all()

    deals_stmt = select(ManualDeal).where(ManualDeal.wallet_address == addr_lower)
    deals_res = await db.execute(deals_stmt)
    manual_deals = deals_res.scalars().all()

    pos_data = []
    if not positions and not manual_deals:
        try:
            pos_data = await indexer_service.fetch_onchain_holdings(addr_lower)
        except Exception as e:
            logger.warning(f"Failed to fetch onchain holdings in risk/portfolio: {e}")
            pos_data = []
    else:
        for p in positions:
            asset_stmt = select(Asset).where(Asset.id == p.asset_id)
            asset_res = await db.execute(asset_stmt)
            asset = asset_res.scalar_one_or_none()

            pos_data.append({
                "symbol": asset.symbol if asset else p.asset_id,
                "asset_class": asset.asset_class if asset else "crypto",
                "quantity": float(p.quantity),
                "unit_price_usd": float(p.unit_price_usd),
                "total_value_usd": float(p.total_value_usd),
                "trade_type": "spot"
            })

        for deal in manual_deals:
            price, _, _ = await oracle_service.get_price(deal.asset_name)
            qty = float(deal.quantity) if deal.side == "buy" else -float(deal.quantity)
            val = abs(qty) * price
            pos_data.append({
                "symbol": deal.asset_name.upper(),
                "asset_class": deal.asset_class or "crypto",
                "quantity": qty,
                "unit_price_usd": price,
                "total_value_usd": val,
                "trade_type": deal.trade_type or "spot"
            })

    profile = await compute_portfolio_risk_profile(
        positions_data=pos_data,
        lookback_days=payload.lookback_days,
        risk_free_rate=settings.RISK_FREE_RATE
    )

    return PortfolioRiskResponse(
        wallet_address=addr_lower,
        net_delta=profile["net_delta"],
        net_gamma=profile["net_gamma"],
        net_vega=profile["net_vega"],
        sharpe_ratio=profile["sharpe_ratio"],
        treynor_ratio=profile["treynor_ratio"],
        assets=profile["assets"],
        covariance_matrix=profile["covariance_matrix"],
        correlation_matrix=profile["correlation_matrix"]
    )

@router.post("/report", response_model=RiskReportResponse)
async def generate_risk_report(
    payload: RiskReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates institutional Risk Report with 1-day 95% & 99% VaR,
    Expected Shortfall (CVaR), and actionable rebalancing recommendations.
    """
    addr_lower = payload.wallet_address.lower()

    # Query active positions
    stmt = select(Position).where(Position.wallet_address == addr_lower)
    result = await db.execute(stmt)
    positions = result.scalars().all()

    deals_stmt = select(ManualDeal).where(ManualDeal.wallet_address == addr_lower)
    deals_res = await db.execute(deals_stmt)
    manual_deals = deals_res.scalars().all()

    pos_data = []
    total_val = 0.0
    if not positions and not manual_deals:
        try:
            pos_data = await indexer_service.fetch_onchain_holdings(addr_lower)
            total_val = sum([p["total_value_usd"] for p in pos_data])
        except Exception as e:
            logger.warning(f"Failed to fetch onchain holdings in risk/report: {e}")
            pos_data = []
            total_val = 0.0
    else:
        for p in positions:
            asset_stmt = select(Asset).where(Asset.id == p.asset_id)
            asset_res = await db.execute(asset_stmt)
            asset = asset_res.scalar_one_or_none()
            val = float(p.total_value_usd)
            total_val += val

            pos_data.append({
                "symbol": asset.symbol if asset else p.asset_id,
                "asset_class": asset.asset_class if asset else "crypto",
                "quantity": float(p.quantity),
                "unit_price_usd": float(p.unit_price_usd),
                "total_value_usd": val,
                "trade_type": "spot"
            })

        for deal in manual_deals:
            price, _, _ = await oracle_service.get_price(deal.asset_name)
            qty = float(deal.quantity) if deal.side == "buy" else -float(deal.quantity)
            val = abs(qty) * price
            total_val += val

            pos_data.append({
                "symbol": deal.asset_name.upper(),
                "asset_class": deal.asset_class or "crypto",
                "quantity": qty,
                "unit_price_usd": price,
                "total_value_usd": val,
                "trade_type": deal.trade_type or "spot"
            })

    # Portfolio Greeks & Volatility
    profile = await compute_portfolio_risk_profile(pos_data)
    port_daily_vol = profile.get("portfolio_volatility", 0.50) / (365.0 ** 0.5)
    port_daily_ret = profile.get("portfolio_return", 0.10) / 365.0

    # Tail-Risk VaR & Expected Shortfall
    tail_risk = calculate_tail_risk(
        portfolio_value_usd=total_val,
        portfolio_daily_return=port_daily_ret,
        portfolio_daily_vol=port_daily_vol
    )

    # Rebalance Suggestions
    rebalance_suggestions = generate_rebalance_suggestions(
        positions_data=pos_data,
        total_portfolio_value=total_val,
        current_var_95=tail_risk["var_95_usd"]
    )

    # Persist Report in database
    report_id = str(uuid.uuid4())
    report_entity = RiskReport(
        id=report_id,
        wallet_address=addr_lower,
        net_delta=profile["net_delta"],
        net_gamma=profile["net_gamma"],
        net_vega=profile["net_vega"],
        var_95_usd=tail_risk["var_95_usd"],
        var_99_usd=tail_risk["var_99_usd"],
        es_95_usd=tail_risk["es_95_usd"],
        es_99_usd=tail_risk["es_99_usd"],
        sharpe_ratio=profile["sharpe_ratio"],
        treynor_ratio=profile["treynor_ratio"],
        matrix_snapshot={"assets": profile["assets"], "covariance": profile["covariance_matrix"]}
    )
    db.add(report_entity)
    await db.commit()

    return RiskReportResponse(
        report_id=report_id,
        timestamp=datetime.utcnow(),
        var_95_usd=tail_risk["var_95_usd"],
        var_99_usd=tail_risk["var_99_usd"],
        es_95_usd=tail_risk["es_95_usd"],
        es_99_usd=tail_risk["es_99_usd"],
        rebalancing_suggestions=[
            RebalanceAction(
                action_type=s["action_type"],
                asset_id=s["asset_id"],
                target_delta_usd=s["target_delta_usd"],
                rationale=s["rationale"],
                recommended_venue=s["recommended_venue"]
            )
            for s in rebalance_suggestions
        ]
    )
