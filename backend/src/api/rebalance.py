import logging
from fastapi import APIRouter, HTTPException
from backend.src.models.schemas import RebalanceQuoteRequest, RebalanceQuoteResponse
from backend.src.services.swaps import swap_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/quote", response_model=RebalanceQuoteResponse)
async def get_rebalance_swap_quote(payload: RebalanceQuoteRequest):
    """
    Fetches read-only swap quotes from 1inch Fusion or Uniswap.
    CONSTITUTIONAL RULE: This endpoint produces an un-signed transaction for client wallet review.
    It NEVER broadcasts or executes trades automatically.
    """
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
        unsigned_tx=quote["unsigned_tx"]
    )
