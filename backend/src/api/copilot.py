import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.src.core.database import get_db
from backend.src.models.entities import Position, Asset
from backend.src.models.schemas import CopilotChatRequest, CopilotChatResponse
from backend.src.services.gemini import gemini_copilot
from backend.src.services.indexer import indexer_service
from backend.src.math.portfolio_risk import compute_portfolio_risk_profile

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=CopilotChatResponse)
async def chat_with_copilot(
    payload: CopilotChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Sends user query to Gemini AI Copilot grounded in the user's active portfolio risk metrics.
    Can explain Greeks, VaR, correlations, and propose (never execute) rebalancing trades.
    """
    addr_lower = payload.wallet_address.lower()

    # Query active positions
    stmt = select(Position).where(Position.wallet_address == addr_lower)
    result = await db.execute(stmt)
    positions = result.scalars().all()

    pos_data = []
    total_val = 0.0
    if not positions:
        pos_data = await indexer_service.fetch_onchain_holdings(addr_lower)
        total_val = sum([p["total_value_usd"] for p in pos_data])
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

    # Portfolio Greeks
    risk_profile = await compute_portfolio_risk_profile(pos_data)

    portfolio_context = {
        "total_value_usd": total_val,
        "positions_count": len(pos_data),
        "assets": [p["symbol"] for p in pos_data],
        "positions": pos_data
    }

    result = await gemini_copilot.chat(
        wallet_address=addr_lower,
        user_message=payload.message,
        portfolio_context=portfolio_context,
        risk_context=risk_profile
    )

    return CopilotChatResponse(
        response_text=result["response_text"],
        tool_calls_executed=result["tool_calls_executed"],
        proposed_rebalance=result["proposed_rebalance"]
    )
