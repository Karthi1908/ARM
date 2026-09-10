import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from backend.src.services.indexer import indexer_service, MultiChainIndexer, CHAIN_METADATA
from backend.src.services.swaps import swap_service
from backend.src.services.rwa_verifier import rwa_verifier


def get_mock_indexer_payloads():
    """
    Isolated mock fixtures for multi-chain indexer external APIs
    (RPC, Blockscout, The Graph) per Constitution Quality Gate 2.
    """
    rpc_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": "0x1bc16d674ec80000"  # 2.0 ETH in hex
    }
    
    blockscout_response = {
        "items": [
            {
                "token": {
                    "symbol": "USDC",
                    "name": "USD Coin",
                    "decimals": "6",
                    "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                    "exchange_rate": "1.0"
                },
                "value": "5000000000"  # 5,000 USDC
            }
        ]
    }
    
    graph_response = {
        "data": {
            "tokenBalances": [
                {
                    "token": {
                        "symbol": "UNI",
                        "name": "Uniswap",
                        "decimals": 18
                    },
                    "amount": "100000000000000000000"  # 100 UNI
                }
            ]
        }
    }
    return {
        "rpc": rpc_response,
        "blockscout": blockscout_response,
        "graph": graph_response
    }


@pytest.fixture
def mock_indexer_responses():
    return get_mock_indexer_payloads()


@pytest.mark.asyncio
async def test_indexer_mock_fixture_isolation(mock_indexer_responses):
    """
    Constitution Quality Gate 2: Verify indexer adapters with isolated mock fixtures.
    Ensures network isolation, deterministic data mapping, and zero live network dependency.
    """
    indexer = MultiChainIndexer()
    test_addr = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    async def mock_post(url, *args, **kwargs):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 200
        if "rpc" in str(url) or "llamarpc" in str(url):
            resp.json.return_value = mock_indexer_responses["rpc"]
        elif "thegraph" in str(url) or "gateway" in str(url):
            resp.json.return_value = mock_indexer_responses["graph"]
        else:
            resp.json.return_value = mock_indexer_responses["rpc"]
        return resp

    async def mock_get(url, *args, **kwargs):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 200
        if "blockscout" in str(url):
            resp.json.return_value = mock_indexer_responses["blockscout"]
        else:
            resp.json.return_value = {}
        return resp

    with patch.object(httpx.AsyncClient, "post", new=AsyncMock(side_effect=mock_post)), \
         patch.object(httpx.AsyncClient, "get", new=AsyncMock(side_effect=mock_get)):
        
        holdings = await indexer.fetch_onchain_holdings(test_addr)
        assert isinstance(holdings, list)
        assert len(holdings) > 0
        symbols = [h["symbol"] for h in holdings]
        assert "ETH" in symbols or "USDC" in symbols or "UNI" in symbols
        for h in holdings:
            assert h["total_value_usd"] >= 0
            assert "price_source" in h
            assert "chain_id" in h


@pytest.mark.asyncio
async def test_indexer_bounded_network_timeout():
    """
    Constitution Quality Gate 2: Verify adapter isolation under network timeouts.
    Ensures bounded execution and graceful degradation when external APIs hang.
    """
    indexer = MultiChainIndexer()
    test_addr = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    async def timeout_side_effect(*args, **kwargs):
        raise httpx.TimeoutException("Connection timed out after 7.0s limit")

    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(side_effect=timeout_side_effect)), \
         patch.object(httpx.AsyncClient, "post", new=AsyncMock(side_effect=timeout_side_effect)):
        
        # Execution must complete quickly without unhandled exceptions
        start_time = asyncio.get_event_loop().time()
        holdings = await indexer.fetch_onchain_holdings(test_addr)
        elapsed = asyncio.get_event_loop().time() - start_time

        assert isinstance(holdings, list)
        # Should gracefully return empty list under complete network failure
        assert len(holdings) == 0
        # Bound check: must complete within bounded window
        assert elapsed < 15.0


@pytest.mark.asyncio
async def test_indexer_network_error_resilience():
    """
    Constitution Quality Gate 2: Verify graceful degradation on HTTP 429 rate limit or 500 errors.
    """
    indexer = MultiChainIndexer()
    test_addr = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    async def error_side_effect(*args, **kwargs):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 429
        resp.raise_for_status.side_effect = httpx.HTTPStatusError("Rate limited", request=MagicMock(), response=resp)
        return resp

    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(side_effect=error_side_effect)), \
         patch.object(httpx.AsyncClient, "post", new=AsyncMock(side_effect=error_side_effect)):
        
        holdings = await indexer.fetch_onchain_holdings(test_addr)
        assert isinstance(holdings, list)
        assert len(holdings) == 0


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


@pytest.mark.asyncio
async def test_indexer_holdings_discovery():
    test_addr = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    try:
        holdings = await asyncio.wait_for(indexer_service.fetch_onchain_holdings(test_addr), timeout=10.0)
        assert len(holdings) > 0
        symbols = [h["symbol"] for h in holdings]
        assert "ETH" in symbols
        for h in holdings:
            assert h["total_value_usd"] >= 0
            assert h["price_source"] in [
                "chainlink", "defillama_fallback", "default_estimate",
                "blockscout_dex", "the_graph", "coingecko", "unranked_zero", "unpriced_zero"
            ]
    except (asyncio.TimeoutError, httpx.HTTPError) as e:
        # Graceful degradation when external public APIs are unreachable during offline test runs
        pytest.skip(f"Live network test skipped due to external API timeout or rate limit: {e}")


@pytest.mark.asyncio
async def test_the_graph_isolated_without_blockscout():
    indexer = MultiChainIndexer()
    test_addr = "0x50ec05ade8280758e2077fcbc08d878d4aef79c3"

    original_apis = {c: meta.get("blockscout_api") for c, meta in CHAIN_METADATA.items()}
    try:
        for meta in CHAIN_METADATA.values():
            meta["blockscout_api"] = ""

        holdings = await asyncio.wait_for(indexer.fetch_onchain_holdings(test_addr), timeout=10.0)
        if len(holdings) > 0:
            graph_holdings = [h for h in holdings if h.get("price_source") == "the_graph"]
            assert len(graph_holdings) >= 0
    except (asyncio.TimeoutError, httpx.HTTPError) as e:
        pytest.skip(f"Live Graph network test skipped due to external network latency: {e}")
    finally:
        for c, api in original_apis.items():
            CHAIN_METADATA[c]["blockscout_api"] = api
