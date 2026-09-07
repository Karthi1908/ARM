import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.src.core.database import get_db
from backend.src.models.entities import ManualDeal
from backend.src.models.schemas import ManualDealCreate, ManualDealResponse
from backend.src.services.portfolio_aggregator import portfolio_aggregator
from backend.src.services.rwa_verifier import rwa_verifier

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{wallet_address}/deals", response_model=List[ManualDealResponse])
async def list_deals(
    wallet_address: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all manual blotter trades recorded by the user."""
    addr_lower = wallet_address.lower()
    stmt = select(ManualDeal).where(ManualDeal.wallet_address == addr_lower).order_by(ManualDeal.trade_date.desc())
    result = await db.execute(stmt)
    deals = result.scalars().all()

    return [
        ManualDealResponse(
            id=d.id,
            wallet_address=d.wallet_address,
            asset_name=d.asset_name,
            trade_date=d.trade_date,
            side=d.side,
            trade_type=d.trade_type,
            asset_class=d.asset_class,
            settlement_date=d.settlement_date,
            venue=d.venue,
            quantity=float(d.quantity),
            cost_basis_usd=float(d.cost_basis_usd),
            notes=d.notes,
            created_at=d.created_at
        )
        for d in deals
    ]

@router.post("/{wallet_address}/deals", response_model=ManualDealResponse, status_code=201)
async def create_deal(
    wallet_address: str,
    payload: ManualDealCreate,
    db: AsyncSession = Depends(get_db)
):
    """Adds a new manual trade entry (Spot, RWA, or Perps) and recalculates portfolio holdings."""
    addr_lower = wallet_address.lower()

    deal = ManualDeal(
        wallet_address=addr_lower,
        asset_name=payload.asset_name.strip(),
        trade_date=payload.trade_date,
        side=payload.side,
        trade_type=payload.trade_type,
        asset_class=payload.asset_class,
        settlement_date=payload.settlement_date,
        venue=payload.venue.strip(),
        quantity=payload.quantity,
        cost_basis_usd=payload.cost_basis_usd,
        notes=payload.notes
    )

    db.add(deal)
    await db.commit()
    await db.refresh(deal)

    # Blend with on-chain positions
    await portfolio_aggregator.sync_blended_positions(addr_lower, db)

    return ManualDealResponse(
        id=deal.id,
        wallet_address=deal.wallet_address,
        asset_name=deal.asset_name,
        trade_date=deal.trade_date,
        side=deal.side,
        trade_type=deal.trade_type,
        asset_class=deal.asset_class,
        settlement_date=deal.settlement_date,
        venue=deal.venue,
        quantity=float(deal.quantity),
        cost_basis_usd=float(deal.cost_basis_usd),
        notes=deal.notes,
        created_at=deal.created_at
    )

@router.delete("/{wallet_address}/deals/{deal_id}")
async def delete_deal(
    wallet_address: str,
    deal_id: str,
    db: AsyncSession = Depends(get_db)
):
    addr_lower = wallet_address.lower()
    stmt = delete(ManualDeal).where(ManualDeal.id == deal_id, ManualDeal.wallet_address == addr_lower)
    result = await db.execute(stmt)
    await db.commit()

    # Re-blend portfolio
    await portfolio_aggregator.sync_blended_positions(addr_lower, db)
    return {"status": "deleted", "deal_id": deal_id}

@router.get("/rwa-verification/{asset_symbol}")
async def get_rwa_verification(asset_symbol: str):
    """Returns Chainlink Proof of Reserve (PoR) verification metrics for an RWA."""
    return rwa_verifier.verify_asset(asset_symbol)
