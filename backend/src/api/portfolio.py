import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.src.core.database import get_db
from backend.src.models.entities import Position, Asset, ManualDeal
from backend.src.models.schemas import PortfolioResponse, PortfolioSyncResponse, PositionResponse
from backend.src.services.indexer import indexer_service, SUPPORTED_CHAINS
from backend.src.services.oracles import oracle_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{wallet_address}", response_model=PortfolioResponse)
async def get_portfolio(
    wallet_address: str,
    db: AsyncSession = Depends(get_db)
):
    """Fetches consolidated portfolio holdings (both on-chain discovered and manual blotter deals)."""
    addr_lower = wallet_address.lower()

    # Query active positions from database
    stmt = select(Position).where(Position.wallet_address == addr_lower)
    result = await db.execute(stmt)
    positions = result.scalars().all()

    # If no positions exist in DB yet, trigger initial auto-sync
    if not positions:
        holdings = await indexer_service.fetch_onchain_holdings(addr_lower)
        for h in holdings:
            # Ensure asset exists
            asset_stmt = select(Asset).where(Asset.id == h["asset_id"])
            asset_res = await db.execute(asset_stmt)
            if not asset_res.scalar_one_or_none():
                db.add(Asset(
                    id=h["asset_id"],
                    symbol=h["symbol"],
                    name=h["name"],
                    asset_class=h["asset_class"],
                    is_benchmark=(h["asset_id"] == "BTC")
                ))
            
            p = Position(
                wallet_address=addr_lower,
                asset_id=h["asset_id"],
                source_type=h["source_type"],
                chain_id=h["chain_id"],
                quantity=h["quantity"],
                unit_price_usd=h["unit_price_usd"],
                total_value_usd=h["total_value_usd"]
            )
            db.add(p)
        await db.commit()
        # Re-query
        result = await db.execute(stmt)
        positions = result.scalars().all()

    # Format response with asset details
    pos_responses = []
    total_val = 0.0

    for pos in positions:
        asset_stmt = select(Asset).where(Asset.id == pos.asset_id)
        asset_res = await db.execute(asset_stmt)
        asset = asset_res.scalar_one_or_none()
        
        symbol = asset.symbol if asset else pos.asset_id
        name = asset.name if asset else pos.asset_id
        asset_class = asset.asset_class if asset else "crypto"

        val = float(pos.total_value_usd)
        total_val += val

        pos_responses.append(PositionResponse(
            id=pos.id,
            asset_id=pos.asset_id,
            symbol=symbol,
            name=name,
            asset_class=asset_class,
            source_type=pos.source_type,
            chain_id=pos.chain_id,
            quantity=float(pos.quantity),
            unit_price_usd=float(pos.unit_price_usd),
            total_value_usd=val
        ))

    return PortfolioResponse(
        wallet_address=addr_lower,
        total_value_usd=round(total_val, 2),
        positions=pos_responses
    )

@router.post("/{wallet_address}/sync", response_model=PortfolioSyncResponse)
async def sync_portfolio(
    wallet_address: str,
    db: AsyncSession = Depends(get_db)
):
    """Triggers live balance discovery across EVM chains via The Graph & 1inch fallback."""
    addr_lower = wallet_address.lower()

    # Delete previous on-chain discovered positions to refresh
    del_stmt = delete(Position).where(
        Position.wallet_address == addr_lower,
        Position.source_type == "on_chain_discovered"
    )
    await db.execute(del_stmt)

    # Discover latest holdings
    holdings = await indexer_service.fetch_onchain_holdings(addr_lower)
    for h in holdings:
        asset_stmt = select(Asset).where(Asset.id == h["asset_id"])
        asset_res = await db.execute(asset_stmt)
        if not asset_res.scalar_one_or_none():
            db.add(Asset(
                id=h["asset_id"],
                symbol=h["symbol"],
                name=h["name"],
                asset_class=h["asset_class"],
                is_benchmark=(h["asset_id"] == "BTC")
            ))

        db.add(Position(
            wallet_address=addr_lower,
            asset_id=h["asset_id"],
            source_type=h["source_type"],
            chain_id=h["chain_id"],
            quantity=h["quantity"],
            unit_price_usd=h["unit_price_usd"],
            total_value_usd=h["total_value_usd"]
        ))

    await db.commit()

    return PortfolioSyncResponse(
        discovered_count=len(holdings),
        chains_scanned=SUPPORTED_CHAINS,
        synced_at=datetime.utcnow()
    )
