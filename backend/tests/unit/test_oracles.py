import pytest
from backend.src.services.oracles import oracle_service

@pytest.mark.asyncio
async def test_top_200_coingecko_pricing():
    # Top 200 tokens should have positive prices and coingecko source
    price, source, ts = await oracle_service.get_price("ETH")
    assert price > 0.0
    assert source == "coingecko"
    assert ts > 0

    price_btc, source_btc, _ = await oracle_service.get_price("BTC")
    assert price_btc > 1000.0
    assert source_btc == "coingecko"

@pytest.mark.asyncio
async def test_token_aliases():
    # WETH and WBTC should resolve via alias to top 200 assets
    price_weth, source_weth, _ = await oracle_service.get_price("WETH")
    assert price_weth > 0.0
    assert source_weth == "coingecko"

    price_wbtc, source_wbtc, _ = await oracle_service.get_price("WBTC")
    assert price_wbtc > 0.0
    assert source_wbtc == "coingecko"

@pytest.mark.asyncio
async def test_unranked_token_marked_as_zero():
    # Tokens outside top 200 ranking must have price marked as 0.0
    unranked_tokens = ["KICK", "MNE", "BOBA_SPAM_FAKE", "RANDOM_MEME_COIN_999"]
    for sym in unranked_tokens:
        price, source, _ = await oracle_service.get_price(sym)
        assert price == 0.0, f"Token {sym} was expected to have price 0.0, got {price}"
        assert source == "unranked_zero"

@pytest.mark.asyncio
async def test_multiple_prices_resolution():
    res = await oracle_service.get_multiple_prices(["ETH", "KICK", "SOL"])
    assert res["ETH"]["price"] > 0.0
    assert res["ETH"]["source"] == "coingecko"
    assert res["KICK"]["price"] == 0.0
    assert res["KICK"]["source"] == "unranked_zero"
    assert res["SOL"]["price"] > 0.0
    assert res["SOL"]["source"] == "coingecko"
