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
    # Tokens unlisted or outside ranking must have price marked as 0.0 with unpriced/unranked source
    unranked_tokens = ["KICK", "MNE", "BOBA_SPAM_FAKE", "RANDOM_MEME_COIN_999"]
    for sym in unranked_tokens:
        price, source, _ = await oracle_service.get_price(sym)
        assert price == 0.0, f"Token {sym} was expected to have price 0.0, got {price}"
        assert source in ("unpriced_zero", "unranked_zero")

@pytest.mark.asyncio
async def test_multiple_prices_resolution():
    res = await oracle_service.get_multiple_prices(["ETH", "KICK", "SOL"])
    assert res["ETH"]["price"] > 0.0
    assert res["ETH"]["source"] == "coingecko"
    assert res["KICK"]["price"] == 0.0
    assert res["KICK"]["source"] in ("unpriced_zero", "unranked_zero")
    assert res["SOL"]["price"] > 0.0
    assert res["SOL"]["source"] == "coingecko"

def test_coingecko_api_config():
    from backend.src.core.config import settings
    
    # Test Demo Key routing
    settings.COINGECKO_API_KEY = "CG-testdemokey123"
    url, headers = oracle_service._get_api_config()
    assert "api.coingecko.com" in url
    assert headers.get("x-cg-demo-api-key") == "CG-testdemokey123"

    # Test Pro Key routing
    settings.COINGECKO_API_KEY = "pro-key-secret-999"
    url, headers = oracle_service._get_api_config()
    assert "pro-api.coingecko.com" in url
    assert headers.get("x-cg-pro-api-key") == "pro-key-secret-999"

    # Test Public / No Key
    settings.COINGECKO_API_KEY = ""
    url, headers = oracle_service._get_api_config()
    assert "api.coingecko.com" in url
    assert "x-cg-demo-api-key" not in headers
    assert "x-cg-pro-api-key" not in headers

@pytest.mark.asyncio
async def test_zero_valuation_filtered_in_portfolio_risk():
    from backend.src.math.portfolio_risk import compute_portfolio_risk_profile
    
    # Mixed portfolio with 1 priced asset and 2 unpriced ($0) assets
    positions = [
        {
            "symbol": "ETH",
            "unit_price_usd": 2500.0,
            "quantity": 2.0,
            "total_value_usd": 5000.0,
            "asset_class": "crypto",
            "trade_type": "spot"
        },
        {
            "symbol": "SPAM_TOKEN_ZERO",
            "unit_price_usd": 0.0,
            "quantity": 1000.0,
            "total_value_usd": 0.0,
            "asset_class": "crypto",
            "trade_type": "spot"
        },
        {
            "symbol": "TEST_UNPRICED",
            "unit_price_usd": 0.0,
            "quantity": 500.0,
            "total_value_usd": 0.0,
            "asset_class": "crypto",
            "trade_type": "spot"
        }
    ]
    
    res = await compute_portfolio_risk_profile(positions)
    # The zero-value assets must be filtered out so the covariance matrix has only the priced asset
    assert res["assets"] == ["ETH"]
    assert len(res["covariance_matrix"]) == 1
    assert res["net_delta"] > 0
    assert not any(sym in res["assets"] for sym in ["SPAM_TOKEN_ZERO", "TEST_UNPRICED"])
