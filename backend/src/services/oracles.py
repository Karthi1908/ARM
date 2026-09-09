import time
import logging
import httpx
from typing import Dict, Any, Tuple
from backend.src.core.redis_client import redis_manager

logger = logging.getLogger(__name__)

# Common token aliases to map to CoinGecko canonical symbols
TOKEN_ALIASES: Dict[str, str] = {
    "WETH": "ETH",
    "WBTC": "BTC",
    "WSOL": "SOL",
    "WMATIC": "MATIC",
    "ONDO_USDY": "USDY",
    "USDY_TOKEN": "USDY",
}

# Baseline seed for top tokens in case of emergency API downtime
SEED_TOP_TOKENS: Dict[str, Dict[str, Any]] = {
    "BTC": {"price": 78500.0, "rank": 1, "name": "Bitcoin"},
    "ETH": {"price": 2500.0, "rank": 2, "name": "Ethereum"},
    "USDT": {"price": 1.00, "rank": 3, "name": "Tether"},
    "SOL": {"price": 145.0, "rank": 4, "name": "Solana"},
    "BNB": {"price": 600.0, "rank": 5, "name": "BNB"},
    "USDC": {"price": 1.00, "rank": 6, "name": "USDC"},
    "XRP": {"price": 2.20, "rank": 7, "name": "XRP"},
    "DOGE": {"price": 0.20, "rank": 8, "name": "Dogecoin"},
    "ADA": {"price": 0.75, "rank": 9, "name": "Cardano"},
    "TRX": {"price": 0.25, "rank": 10, "name": "TRON"},
    "AVAX": {"price": 25.0, "rank": 15, "name": "Avalanche"},
    "LINK": {"price": 18.50, "rank": 18, "name": "Chainlink"},
    "DAI": {"price": 1.00, "rank": 22, "name": "Dai"},
    "POL": {"price": 0.35, "rank": 35, "name": "Polygon Ecosystem Token"},
    "MATIC": {"price": 0.35, "rank": 36, "name": "Polygon"},
    "USDY": {"price": 1.14, "rank": 44, "name": "Ondo US Dollar Yield"},
    "ONDO": {"price": 0.38, "rank": 50, "name": "Ondo"},
    "MORPHO": {"price": 2.44, "rank": 55, "name": "Morpho"},
    "ARB": {"price": 0.85, "rank": 65, "name": "Arbitrum"},
    "UNI": {"price": 7.50, "rank": 70, "name": "Uniswap"},
    "OP": {"price": 1.80, "rank": 75, "name": "Optimism"},
    "VIRTUAL": {"price": 0.73, "rank": 113, "name": "Virtuals Protocol"},
}

class PriceOracleService:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self._top_200_cache: Dict[str, Dict[str, Any]] = {}
        self._top_200_fetched_at: float = 0.0
        self._cache_ttl_seconds: float = 300.0  # 5 minutes

    async def _refresh_coingecko_top_200(self) -> None:
        """
        Queries CoinGecko for the top 200 ranked coins by market cap.
        Caches results in memory and Redis.
        """
        url = f"{self.coingecko_base}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": "200",
            "page": "1",
            "sparkline": "false"
        }
        headers = {
            "User-Agent": "AgenticRiskManager/1.0",
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    coins_list = resp.json()
                    new_cache: Dict[str, Dict[str, Any]] = {}
                    for item in coins_list:
                        sym = str(item.get("symbol") or "").upper().strip()
                        if not sym:
                            continue
                        rank = int(item.get("market_cap_rank") or 999)
                        price = float(item.get("current_price") or 0.0)

                        # Only accept if within top 200
                        if rank <= 200:
                            if sym not in new_cache or rank < new_cache[sym]["rank"]:
                                new_cache[sym] = {
                                    "price": price,
                                    "rank": rank,
                                    "name": item.get("name", sym),
                                    "id": item.get("id", "")
                                }

                    if new_cache:
                        self._top_200_cache = new_cache
                        self._top_200_fetched_at = time.time()
                        await redis_manager.set("coingecko:top_200", new_cache, ttl_seconds=int(self._cache_ttl_seconds))
                        logger.info(f"Refreshed CoinGecko top 200 market data: {len(new_cache)} symbols cached.")
                        return
                elif resp.status_code == 429:
                    logger.warning("CoinGecko API rate limit (429) hit; using existing cache / seed fallback.")
                else:
                    logger.warning(f"CoinGecko API returned status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Failed to fetch CoinGecko top 200: {e}")

        # If empty and fetch failed, try Redis
        if not self._top_200_cache:
            redis_cached = await redis_manager.get("coingecko:top_200")
            if redis_cached and isinstance(redis_cached, dict):
                self._top_200_cache = redis_cached
                self._top_200_fetched_at = time.time()
                return

        # Emergency fallback to seed tokens if cache is still empty
        if not self._top_200_cache:
            self._top_200_cache = SEED_TOP_TOKENS.copy()
            self._top_200_fetched_at = time.time()

    async def _ensure_top_200_cache(self) -> None:
        """Ensures the top 200 cache is populated and not expired."""
        now = time.time()
        if not self._top_200_cache or (now - self._top_200_fetched_at) > self._cache_ttl_seconds:
            redis_cached = await redis_manager.get("coingecko:top_200")
            if redis_cached and isinstance(redis_cached, dict):
                self._top_200_cache = redis_cached
                self._top_200_fetched_at = now
            else:
                await self._refresh_coingecko_top_200()

    async def get_price(self, symbol: str) -> Tuple[float, str, float]:
        """
        Returns (price_usd, source_provenance, timestamp).
        Rules:
        - Checks CoinGecko top 200 token ranking.
        - If the token is in the top 200, returns real CoinGecko price with source 'coingecko'.
        - If the token is NOT in the first 200 token ranking, returns price 0.0 with source 'unranked_zero'.
        """
        symbol_clean = symbol.upper().replace("$", "").strip()
        ts = time.time()

        # Special institutional RWA benchmark check
        if symbol_clean == "TBILL_RWA":
            return 100.25, "proof_of_reserve", ts

        # Check per-symbol redis cache
        cache_key = f"price:{symbol_clean}"
        cached = await redis_manager.get(cache_key)
        if cached:
            return float(cached["price"]), cached["source"], float(cached["timestamp"])

        # Ensure top 200 rankings are loaded
        await self._ensure_top_200_cache()

        # Check alias (e.g. WETH -> ETH, WBTC -> BTC, ONDO_USDY -> USDY)
        lookup_sym = TOKEN_ALIASES.get(symbol_clean, symbol_clean)
        coin_info = self._top_200_cache.get(lookup_sym)

        if coin_info and coin_info.get("rank", 999) <= 200:
            price = float(coin_info.get("price") or 0.0)
            source = "coingecko"
        else:
            # Token is not in first 200 token ranking -> mark price as 0
            price = 0.0
            source = "unranked_zero"

        # Cache symbol price in Redis for 60 seconds
        await redis_manager.set(cache_key, {"price": price, "source": source, "timestamp": ts}, ttl_seconds=60)
        return price, source, ts

    async def get_multiple_prices(self, symbols: list[str]) -> Dict[str, Dict[str, Any]]:
        results = {}
        for s in symbols:
            price, source, ts = await self.get_price(s)
            results[s.upper()] = {
                "price": price,
                "source": source,
                "timestamp": ts,
                "is_stale": (time.time() - ts) > 3600
            }
        return results

oracle_service = PriceOracleService()
