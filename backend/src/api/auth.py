import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.src.core.database import get_db
from backend.src.models.entities import WalletSession
from backend.src.models.schemas import WalletSessionCreate, WalletSessionResponse

logger = logging.getLogger(__name__)
router = APIRouter()

async def resolve_ens(address: str) -> str | None:
    """Attempts to resolve ENS name for an EVM address using Cloudflare/public ENS API."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"https://api.ensideas.com/ens/resolve/{address}")
            if resp.status_code == 200:
                data = resp.json()
                return data.get("name")
    except Exception as e:
        logger.warning(f"ENS resolution failed for {address}: {e}")
    return None

@router.post("/session", response_model=WalletSessionResponse)
async def create_or_refresh_session(
    payload: WalletSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registers non-custodial wallet session and resolves human-readable ENS."""
    address_lower = payload.address.lower()
    
    # Resolve ENS
    ens_name = await resolve_ens(address_lower)
    
    # Query existing session
    stmt = select(WalletSession).where(WalletSession.address == address_lower)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if session:
        session.last_active_at = datetime.utcnow()
        if ens_name:
            session.ens_name = ens_name
        session.auth_provider = payload.auth_provider
    else:
        session = WalletSession(
            address=address_lower,
            ens_name=ens_name,
            auth_provider=payload.auth_provider
        )
        db.add(session)
        
    await db.commit()
    await db.refresh(session)
    
    return WalletSessionResponse(
        address=session.address,
        ens_name=session.ens_name,
        auth_provider=session.auth_provider,
        created_at=session.created_at
    )
