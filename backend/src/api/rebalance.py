import logging
from fastapi import APIRouter, HTTPException
from backend.src.models.schemas import RebalanceQuoteRequest, RebalanceQuoteResponse
from backend.src.services.swaps import swap_service
from backend.src.services.uniswap_ai import uniswap_ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/quote", response_model=RebalanceQuoteResponse)
async def get_rebalance_swap_quote(payload: RebalanceQuoteRequest):
    """
    Fetches read-only swap quotes from 1inch Fusion or Uniswap AI routing service.
    CONSTITUTIONAL RULE: This endpoint produces an un-signed transaction for client wallet review.
    It NEVER broadcasts or executes trades automatically.
    """
    if payload.venue.lower() == "uniswap":
        quote = await uniswap_ai_service.get_hedge_quote(
            chain_id=payload.chain_id,
            from_token=payload.from_token,
            to_token=payload.to_token,
            amount=payload.amount
        )
        return RebalanceQuoteResponse(
            venue=quote["venue"],
            from_amount=quote["from_amount"],
            to_amount=quote["to_amount"],
            estimated_slippage_bps=quote["estimated_slippage_bps"],
            gas_estimate_usd=quote["gas_estimate_usd"],
            unsigned_tx=quote["unsigned_tx"],
            route_summary=quote.get("route_summary"),
            pool_fee_tier_bps=quote.get("pool_fee_tier_bps"),
            usd_value=quote.get("usd_value")
        )

    quote = await swap_service.get_swap_quote(
        chain_id=payload.chain_id,
        from_token=payload.from_token,
        to_token=payload.to_token,
        amount=payload.amount,
        venue=payload.venue
    )

    return RebalanceQuoteResponse(
        venue=quote["venue"],
        from_amount=quote["from_amount"],
        to_amount=quote["to_amount"],
        estimated_slippage_bps=quote["estimated_slippage_bps"],
        gas_estimate_usd=quote["gas_estimate_usd"],
        unsigned_tx=quote["unsigned_tx"],
        route_summary=None,
        pool_fee_tier_bps=None,
        usd_value=None
    )
