import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.src.models.entities import Position, ManualDeal, Asset
from backend.src.services.oracles import oracle_service

logger = logging.getLogger(__name__)

class PortfolioAggregator:
    """Blends on-chain discovered token holdings with manual blotter entries into unified positions."""

    async def sync_blended_positions(self, wallet_address: str, db: AsyncSession):
        addr_lower = wallet_address.lower()

        # Fetch manual deals
        stmt = select(ManualDeal).where(ManualDeal.wallet_address == addr_lower)
        result = await db.execute(stmt)
        deals = result.scalars().all()

        # Remove previous manual_entry positions for this wallet
        del_stmt = delete(Position).where(
            Position.wallet_address == addr_lower,
            Position.source_type == "manual_entry"
        )
        await db.execute(del_stmt)

        # Aggregate deals by asset_name
        aggregated: dict[str, dict] = {}
        for d in deals:
            asset_key = d.asset_name.upper()
            qty = float(d.quantity) if d.side == "buy" else -float(d.quantity)

            if asset_key not in aggregated:
                aggregated[asset_key] = {
                    "asset_name": d.asset_name,
                    "asset_class": d.asset_class,
                    "net_quantity": 0.0,
                    "weighted_cost": 0.0,
                }
            aggregated[asset_key]["net_quantity"] += qty

        # Insert aggregated manual positions into positions table
        for asset_key, data in aggregated.items():
            net_qty = data["net_quantity"]
            if abs(net_qty) < 1e-9:
                continue

            price, _, _ = await oracle_service.get_price(asset_key)
            total_val = (abs(net_qty) * price) if price > 0 else 0.0

            # Ensure Asset exists
            asset_stmt = select(Asset).where(Asset.id == asset_key)
            asset_res = await db.execute(asset_stmt)
            if not asset_res.scalar_one_or_none():
                db.add(Asset(
                    id=asset_key,
                    symbol=asset_key,
                    name=data["asset_name"],
                    asset_class=data["asset_class"],
                    is_benchmark=(asset_key == "BTC")
                ))

            db.add(Position(
                wallet_address=addr_lower,
                asset_id=asset_key,
                source_type="manual_entry",
                chain_id=None,
                quantity=net_qty,
                unit_price_usd=price,
                total_value_usd=round(total_val, 2)
            ))

        await db.commit()

portfolio_aggregator = PortfolioAggregator()
