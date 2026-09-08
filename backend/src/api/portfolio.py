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
    """Fetches consolidated portfolio holdings (both actual on-chain discovered balances and manual blotter deals)."""
    addr_lower = wallet_address.lower().strip()

    # Query active on-chain discovered positions from database
    stmt = select(Position).where(Position.wallet_address == addr_lower)
    result = await db.execute(stmt)
    positions = result.scalars().all()

    # If no on-chain positions exist in DB yet, trigger initial live auto-discovery
    if not positions:
        holdings = await indexer_service.fetch_onchain_holdings(addr_lower)
        seen_assets = set()
        for h in holdings:
            if h["asset_id"] not in seen_assets:
                seen_assets.add(h["asset_id"])
                asset_stmt = select(Asset).where(Asset.id == h["asset_id"])
                asset_res = await db.execute(asset_stmt)
                if not asset_res.scalar_one_or_none():
                    db.add(Asset(
                        id=h["asset_id"],
                        symbol=h["symbol"],
                        name=h["name"][:120],
                        asset_class=h["asset_class"],
                        is_benchmark=(h["symbol"].upper() == "BTC")
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
        if holdings:
            await db.commit()
            result = await db.execute(stmt)
            positions = result.scalars().all()

    pos_responses = []
    total_val = 0.0

    # 1. On-chain discovered positions
    for pos in positions:
        if pos.source_type != "on_chain_discovered":
            continue
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
            total_value_usd=round(val, 2)
        ))

    # 2. Manual blotter deals
    deals_stmt = select(ManualDeal).where(ManualDeal.wallet_address == addr_lower)
    deals_res = await db.execute(deals_stmt)
    manual_deals = deals_res.scalars().all()

    for deal in manual_deals:
        # Get live or cost-basis price
        price, _, _ = await oracle_service.get_price(deal.asset_name)
        qty = float(deal.quantity) if deal.side == "buy" else -float(deal.quantity)
        val = abs(qty) * price
        total_val += val

        pos_responses.append(PositionResponse(
            id=deal.id,
            asset_id=f"{deal.asset_name.upper()}_MANUAL",
            symbol=deal.asset_name.upper(),
            name=f"{deal.asset_name} ({deal.venue})",
            asset_class=deal.asset_class,
            source_type="manual_entry",
            chain_id=None,
            quantity=qty,
            unit_price_usd=price,
            total_value_usd=round(val, 2)
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
    """Triggers live on-chain balance discovery across EVM chains via public RPCs and Blockscout explorers."""
    addr_lower = wallet_address.lower().strip()

    # Clear previous on-chain discovered positions to refresh with latest chain data
    del_stmt = delete(Position).where(
        Position.wallet_address == addr_lower,
        Position.source_type == "on_chain_discovered"
    )
    await db.execute(del_stmt)

    # Discover live on-chain holdings
    holdings = await indexer_service.fetch_onchain_holdings(addr_lower)
    seen_assets = set()
    for h in holdings:
        if h["asset_id"] not in seen_assets:
            seen_assets.add(h["asset_id"])
            asset_stmt = select(Asset).where(Asset.id == h["asset_id"])
            asset_res = await db.execute(asset_stmt)
            if not asset_res.scalar_one_or_none():
                db.add(Asset(
                    id=h["asset_id"],
                    symbol=h["symbol"],
                    name=h["name"][:120],
                    asset_class=h["asset_class"],
                    is_benchmark=(h["symbol"].upper() == "BTC")
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
