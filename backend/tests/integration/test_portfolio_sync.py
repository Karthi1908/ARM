import pytest
from backend.src.services.indexer import indexer_service
from backend.src.services.swaps import swap_service
from backend.src.services.rwa_verifier import rwa_verifier

@pytest.mark.asyncio
async def test_indexer_holdings_discovery():
    test_addr = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    holdings = await indexer_service.fetch_onchain_holdings(test_addr)
    assert len(holdings) > 0
    symbols = [h["symbol"] for h in holdings]
    assert "ETH" in symbols
    assert "BTC" in symbols
    for h in holdings:
        assert h["total_value_usd"] > 0
        assert h["price_source"] in ["chainlink", "defillama_fallback", "default_estimate"]

@pytest.mark.asyncio
async def test_swap_quote_non_custodial():
    quote = await swap_service.get_swap_quote(
        chain_id=1,
        from_token="ETH",
        to_token="ONDO_USDY",
        amount="1.5",
        venue="1inch"
    )
    assert quote["venue"] == "1inch"
    assert quote["requires_user_signature"] is True
    assert "unsigned_tx" in quote
    assert quote["unsigned_tx"]["to"].startswith("0x")

def test_rwa_verifier_chainlink_por():
    # Ondo USDY verification
    res_usdy = rwa_verifier.verify_asset("ONDO_USDY")
    assert res_usdy["verified"] is True
    assert "Proof of Reserve" in res_usdy["oracle_standard"]
    assert res_usdy["reserve_ratio"] > 1.0

    # Unverified asset
    res_unknown = rwa_verifier.verify_asset("UNKNOWN_COIN")
    assert res_unknown["verified"] is False
