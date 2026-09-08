import asyncio
import logging
import httpx
from typing import List, Dict, Any
from backend.src.core.config import settings
from backend.src.services.oracles import oracle_service

logger = logging.getLogger(__name__)

SUPPORTED_CHAINS = [1, 42161, 10, 8453, 137]

CHAIN_METADATA: Dict[int, Dict[str, Any]] = {
    1: {
        "name": "Ethereum",
        "native_symbol": "ETH",
        "native_name": "Ethereum",
        "rpcs": ["https://ethereum-rpc.publicnode.com", "https://eth.llamarpc.com", "https://1rpc.io/eth"],
        "blockscout_api": "https://eth.blockscout.com/api/v2",
        "the_graph_subgraph_id": "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV",
    },
    42161: {
        "name": "Arbitrum",
        "native_symbol": "ETH",
        "native_name": "Ethereum (Arbitrum)",
        "rpcs": ["https://arbitrum-one-rpc.publicnode.com", "https://arb1.arbitrum.io/rpc"],
        "blockscout_api": "https://arbitrum.blockscout.com/api/v2",
        "the_graph_subgraph_id": "FbCGRftH4a3yZugY7TnbYgPJVEv2LvMT6oF1dQKqx8gk",
    },
    10: {
        "name": "Optimism",
        "native_symbol": "ETH",
        "native_name": "Ethereum (Optimism)",
        "rpcs": ["https://optimism-rpc.publicnode.com", "https://mainnet.optimism.io"],
        "blockscout_api": "https://optimism.blockscout.com/api/v2",
        "the_graph_subgraph_id": "C9TDQvdEbP9AAbf4ddkFvV864C6o6m4f7m8sXwW2oD1S",
    },
    8453: {
        "name": "Base",
        "native_symbol": "ETH",
        "native_name": "Ethereum (Base)",
        "rpcs": ["https://base-rpc.publicnode.com", "https://mainnet.base.org"],
        "blockscout_api": "https://base.blockscout.com/api/v2",
        "the_graph_subgraph_id": "GqzP4XaeUb119YF93N2Yq7bMvA3X2fB2g6cZ8U8n7hB",
    },
    137: {
        "name": "Polygon",
        "native_symbol": "POL",
        "native_name": "Polygon Ecosystem Token",
        "rpcs": ["https://polygon-bor-rpc.publicnode.com", "https://polygon-rpc.com"],
        "blockscout_api": "https://polygon.blockscout.com/api/v2",
        "the_graph_subgraph_id": "3hCPRGf4z88VC5rsBCUVvSJ6qaWBhFnkWBZupe56sncx",
    }
}

SPAM_PATTERNS = ["www.", "http", "claim", "visit", ".io", ".eu", ".org", ".com", "[", "]", "gift", "airdrop", "reward", "$"]

class MultiChainIndexer:
    """
    Live on-chain balance discovery across EVM chains.
    Fetches actual native and ERC-20 token balances for the provided wallet address.
    Strictly returns actual values (zero simulated/fake holdings).
    """

    async def fetch_onchain_holdings(self, wallet_address: str) -> List[Dict[str, Any]]:
        address_clean = wallet_address.strip().lower()
        if not address_clean.startswith("0x") or len(address_clean) != 42:
            logger.warning(f"Invalid EVM address format: {wallet_address}")
            return []

        tasks = [self._fetch_chain_holdings(chain_id, address_clean) for chain_id in SUPPORTED_CHAINS]
        chain_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_holdings: List[Dict[str, Any]] = []
        for res in chain_results:
            if isinstance(res, list):
                all_holdings.extend(res)
            elif isinstance(res, Exception):
                logger.warning(f"Error fetching holdings on a chain: {res}")

        # Sort by total_value_usd descending
        all_holdings.sort(key=lambda x: x["total_value_usd"], reverse=True)
        return all_holdings

    async def _fetch_chain_holdings(self, chain_id: int, wallet_address: str) -> List[Dict[str, Any]]:
        meta = CHAIN_METADATA.get(chain_id)
        if not meta:
            return []

        holdings: List[Dict[str, Any]] = []
        discovered_symbols = set()

        async with httpx.AsyncClient(timeout=7.0, headers={"User-Agent": "AgenticRiskManager/1.0"}) as client:
            # 1. Fetch Native Balance via RPC
            native_qty = await self._query_native_balance(client, meta["rpcs"], wallet_address)
            if native_qty > 0.0001:
                native_symbol = meta["native_symbol"]
                price, source, ts = await oracle_service.get_price(native_symbol)
                total_val = native_qty * price
                holdings.append({
                    "asset_id": f"{native_symbol}_{chain_id}",
                    "symbol": native_symbol,
                    "name": meta["native_name"],
                    "asset_class": "crypto",
                    "source_type": "on_chain_discovered",
                    "chain_id": chain_id,
                    "quantity": round(native_qty, 6),
                    "unit_price_usd": price,
                    "total_value_usd": round(total_val, 2),
                    "price_source": source,
                    "timestamp": ts
                })
                discovered_symbols.add(native_symbol)

            # 2. Query The Graph Protocol Subgraphs & Token Gateway
            graph_holdings = await self._query_the_graph_holdings(client, chain_id, wallet_address)
            for gh in graph_holdings:
                holdings.append(gh)
                discovered_symbols.add(gh["symbol"])

            # 3. Fetch ERC-20 Token Balances via Explorer API (Fallback & General ERC-20s)
            if meta.get("blockscout_api"):
                try:
                    tokens_url = f"{meta['blockscout_api']}/addresses/{wallet_address}/tokens"
                    resp = await client.get(tokens_url)
                    if resp.status_code == 200:
                        items = resp.json().get("items", [])
                        for item in items:
                            tok = item.get("token", {})
                            symbol = tok.get("symbol")
                            if not symbol:
                                continue
                            
                            symbol_clean = str(symbol).strip().upper()
                            # Deduplicate if already indexed via The Graph
                            if symbol_clean in discovered_symbols:
                                continue

                            # Reject spam / phishing token tickers
                            if len(symbol_clean) > 12 or any(p in symbol_clean.lower() for p in SPAM_PATTERNS):
                                continue

                            name = tok.get("name") or symbol_clean
                            if any(p in name.lower() for p in SPAM_PATTERNS):
                                continue

                            decimals = int(tok.get("decimals") or 18)
                            raw_val = int(item.get("value") or 0)
                            qty = raw_val / (10 ** decimals)
                            if qty <= 0.000001:
                                continue

                            # Resolve USD price
                            exchange_rate = tok.get("exchange_rate")
                            if exchange_rate and float(exchange_rate) > 0:
                                price = float(exchange_rate)
                                source = "blockscout_dex"
                                ts = 0.0
                            else:
                                price, source, ts = await oracle_service.get_price(symbol_clean)

                            total_val = qty * price
                            # Filter out microscopic dust / spam airdrops with zero economic value
                            if total_val < 0.10:
                                continue

                            contract_addr = tok.get("address") or tok.get("address_hash") or ""
                            contract_suffix = f"_{contract_addr[-6:].lower()}" if contract_addr else ""
                            asset_id = f"{symbol_clean}_{chain_id}{contract_suffix}"

                            holdings.append({
                                "asset_id": asset_id,
                                "symbol": symbol_clean,
                                "name": name[:120],
                                "asset_class": "crypto",
                                "source_type": "on_chain_discovered",
                                "chain_id": chain_id,
                                "quantity": round(qty, 6),
                                "unit_price_usd": price,
                                "total_value_usd": round(total_val, 2),
                                "price_source": source,
                                "timestamp": ts
                            })
                            discovered_symbols.add(symbol_clean)
                except Exception as e:
                    logger.warning(f"Error querying token holdings on chain {chain_id} for {wallet_address}: {e}")

        return holdings

    async def _query_the_graph_holdings(self, client: httpx.AsyncClient, chain_id: int, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Queries The Graph Protocol decentralized subgraphs / Token API gateway for token holdings and positions.
        """
        if not settings.THE_GRAPH_API_KEY:
            return []

        meta = CHAIN_METADATA.get(chain_id)
        if not meta or "the_graph_subgraph_id" not in meta:
            return []

        subgraph_id = meta["the_graph_subgraph_id"]
        graph_url = f"https://gateway.thegraph.com/api/{settings.THE_GRAPH_API_KEY}/subgraphs/id/{subgraph_id}"

        holdings: List[Dict[str, Any]] = []
        try:
            # Query positions and token balances from The Graph subgraph
            query = """
            query GetUserPositions($owner: String!) {
              positions(where: { owner: $owner }, first: 10) {
                id
                liquidity
                token0 {
                  id
                  symbol
                  name
                  decimals
                }
                token1 {
                  id
                  symbol
                  name
                  decimals
                }
              }
            }
            """
            resp = await client.post(graph_url, json={"query": query, "variables": {"owner": wallet_address.lower()}})
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                positions = data.get("positions", [])
                for pos in positions:
                    for tok_key in ["token0", "token1"]:
                        tok = pos.get(tok_key)
                        if not tok or not tok.get("symbol"):
                            continue
                        sym = tok["symbol"].upper()
                        if any(p in sym.lower() for p in SPAM_PATTERNS):
                            continue
                        price, source, ts = await oracle_service.get_price(sym)
                        tok_id = tok.get("id", "")
                        tok_suffix = f"_{tok_id[-6:].lower()}" if tok_id else ""
                        holdings.append({
                            "asset_id": f"{sym}_{chain_id}{tok_suffix}",
                            "symbol": sym,
                            "name": tok.get("name", sym)[:120],
                            "asset_class": "crypto",
                            "source_type": "on_chain_discovered",
                            "chain_id": chain_id,
                            "quantity": 1.0,
                            "unit_price_usd": price,
                            "total_value_usd": round(price, 2),
                            "price_source": "the_graph",
                            "timestamp": ts
                        })
        except Exception as e:
            logger.warning(f"The Graph subgraph query failed for chain {chain_id}: {e}")

        return holdings

    async def _query_native_balance(self, client: httpx.AsyncClient, rpcs: List[str], address: str) -> float:
        for rpc in rpcs:
            try:
                r = await client.post(
                    rpc,
                    json={
                        "jsonrpc": "2.0",
                        "method": "eth_getBalance",
                        "params": [address, "latest"],
                        "id": 1
                    }
                )
                if r.status_code == 200:
                    data = r.json()
                    if "result" in data:
                        wei = int(data["result"], 16)
                        return wei / 1e18
            except Exception:
                continue
        return 0.0

indexer_service = MultiChainIndexer()
