import asyncio
import json
from httpx import AsyncClient, ASGITransport
from backend.src.main import app
from backend.src.core.database import init_db
from backend.src.core.config import settings

async def run_graph_only_test():
    print("============================================================", flush=True)
    print(" SWITCHING CONFIGURATION: ONLY THE GRAPH ENABLED", flush=True)
    print(" (RPC Query: DISABLED | Blockscout API: DISABLED)", flush=True)
    print("============================================================\n", flush=True)

    # Force toggles: ONLY The Graph enabled
    settings.ENABLE_RPC_DISCOVERY = False
    settings.ENABLE_BLOCKSCOUT_DISCOVERY = False
    settings.ENABLE_THE_GRAPH = True

    print(f"• settings.ENABLE_THE_GRAPH:          {settings.ENABLE_THE_GRAPH}", flush=True)
    print(f"• settings.ENABLE_RPC_DISCOVERY:      {settings.ENABLE_RPC_DISCOVERY}", flush=True)
    print(f"• settings.ENABLE_BLOCKSCOUT_DISCOVERY: {settings.ENABLE_BLOCKSCOUT_DISCOVERY}", flush=True)
    print(f"• settings.THE_GRAPH_API_KEY:         {settings.THE_GRAPH_API_KEY[:6]}... (active)\n", flush=True)

    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        # 1. Health check
        res = await client.get("/health")
        print(f"[1] Health Check Status: {res.status_code} | Service: {res.json().get('service')}\n", flush=True)
        assert res.status_code == 200

        wallets_to_test = [
            ("0x50ec05ade8280758e2077fcbc08d878d4aef79c3", "The Graph Active Position Holder"),
            ("0x8074059191f858c7905E2c6941b5452724eD2cAb", "Target Wallet"),
        ]

        for wallet_addr, label in wallets_to_test:
            print(f"------------------------------------------------------------", flush=True)
            print(f" TESTING: {label} ({wallet_addr})", flush=True)
            print(f"------------------------------------------------------------", flush=True)

            # Sync portfolio via API
            print(f"--> Triggering POST /api/v1/portfolio/{wallet_addr}/sync ...", flush=True)
            sync_res = await client.post(f"/api/v1/portfolio/{wallet_addr}/sync")
            print(f"    Sync Status: {sync_res.status_code}")
            sync_data = sync_res.json()
            print(f"    Discovered Count: {sync_data.get('discovered_count')}")
            print(f"    Chains Scanned:   {sync_data.get('chains_scanned')}\n", flush=True)
            assert sync_res.status_code == 200

            # Query portfolio via API
            print(f"--> Fetching GET /api/v1/portfolio/{wallet_addr} ...", flush=True)
            port_res = await client.get(f"/api/v1/portfolio/{wallet_addr}")
            print(f"    Portfolio Status: {port_res.status_code}")
            port_data = port_res.json()
            total_val = port_data.get("total_value_usd", 0)
            positions = port_data.get("positions", [])
            print(f"    Total Portfolio Value: ${total_val:,.2f}")
            print(f"    Total Positions Found: {len(positions)}")

            for idx, p in enumerate(positions, 1):
                print(f"      {idx}. {p['symbol']} ({p['name']}) | Qty: {p['quantity']} | Unit: ${p['unit_price_usd']:,.2f} | Total: ${p['total_value_usd']:,.2f} | Chain: {p['chain_id']}")
            print(flush=True)
            assert port_res.status_code == 200

            # If holdings exist from The Graph, test Portfolio Risk and Report calculation
            if len(positions) > 0:
                print(f"--> Testing Risk Engine with pure Graph positions ...", flush=True)
                risk_res = await client.post("/api/v1/risk/portfolio", json={"wallet_address": wallet_addr})
                print(f"    Portfolio Risk Status: {risk_res.status_code}")
                if risk_res.status_code == 200:
                    risk_data = risk_res.json()
                    print(f"    Net Delta: {risk_data.get('net_delta'):,.2f} | Sharpe: {risk_data.get('sharpe_ratio'):.4f} | Treynor: {risk_data.get('treynor_ratio'):.4f}")
                    print(f"    Assets in Matrix: {risk_data.get('assets')}")

                # Risk Report
                report_res = await client.post("/api/v1/risk/report", json={"wallet_address": wallet_addr})
                print(f"    Risk Report Status: {report_res.status_code}")
                if report_res.status_code == 200:
                    report_data = report_res.json()
                    print(f"    1-Day 95% VaR: ${report_data.get('var_95_usd', 0):,.2f} | 95% CVaR: ${report_data.get('es_95_usd', 0):,.2f}")

                # AI Copilot chat
                copilot_res = await client.post("/api/v1/copilot/chat", json={
                    "wallet_address": wallet_addr,
                    "message": "Summarize my holdings and risk."
                })
                print(f"    Copilot Status: {copilot_res.status_code}")
                if copilot_res.status_code == 200:
                    print(f"    Copilot Summary:\n    {copilot_res.json().get('response_text')[:180]}...\n")

    # Reset toggles to default
    settings.ENABLE_RPC_DISCOVERY = True
    settings.ENABLE_BLOCKSCOUT_DISCOVERY = True
    settings.ENABLE_THE_GRAPH = True

    print("============================================================", flush=True)
    print(" TEST COMPLETED: APP VERIFIED WITH ONLY THE GRAPH PROTOCOL", flush=True)
    print("============================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_graph_only_test())
