import asyncio
import json
import sys
from datetime import date
from httpx import AsyncClient, ASGITransport
from backend.src.main import app
from backend.src.core.database import init_db

TEST_WALLET = "0x8074059191f858c7905E2c6941b5452724eD2cAb"

async def run_e2e_testing():
    print("============================================================", flush=True)
    print(f" STARTING END-TO-END TESTING FOR WALLET:", flush=True)
    print(f" {TEST_WALLET}", flush=True)
    print("============================================================\n", flush=True)

    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=120.0) as client:
        # 1. Health Check
        print("--- [STEP 1: Health Check] ---", flush=True)
        res = await client.get("/health")
        print(f"Status: {res.status_code}", flush=True)
        print(f"Response: {res.json()}\n", flush=True)
        assert res.status_code == 200

        # 2. Portfolio Sync Endpoint (Populates DB with on-chain holdings)
        print("--- [STEP 2: POST /api/v1/portfolio/{wallet}/sync] ---", flush=True)
        sync_res = await client.post(f"/api/v1/portfolio/{TEST_WALLET}/sync")
        print(f"Status: {sync_res.status_code}", flush=True)
        sync_data = sync_res.json()
        print(f"Response: {json.dumps(sync_data, indent=2, default=str)}\n", flush=True)
        assert sync_res.status_code == 200

        # 3. Consolidated Portfolio Query Endpoint
        print("--- [STEP 3: GET /api/v1/portfolio/{wallet}] ---", flush=True)
        port_res = await client.get(f"/api/v1/portfolio/{TEST_WALLET}")
        print(f"Status: {port_res.status_code}", flush=True)
        port_data = port_res.json()
        print(f"Total Value USD: ${port_data.get('total_value_usd', 0):,.2f}", flush=True)
        print(f"Positions Count: {len(port_data.get('positions', []))}", flush=True)
        for p in port_data.get("positions", [])[:10]:
            print(f"  * {p['symbol']} ({p['name']}) | Qty: {p['quantity']} | Unit: ${p['unit_price_usd']:,.2f} | Value: ${p['total_value_usd']:,.2f} | Chain: {p['chain_id']}", flush=True)
        if len(port_data.get("positions", [])) > 10:
            print(f"  ... and {len(port_data.get('positions', [])) - 10} more holdings", flush=True)
        print(flush=True)
        assert port_res.status_code == 200
        assert len(port_data.get("positions", [])) > 0

        # 4. Insert Manual Blotter Deal to verify Hybrid Aggregation (Off-Chain CeFi / RWA)
        print(f"--- [STEP 4: POST /api/v1/blotter/{TEST_WALLET}/deals (Adding CeFi/RWA manual position)] ---", flush=True)
        deal_payload = {
            "asset_name": "ONDO_USDY",
            "trade_date": str(date.today()),
            "side": "buy",
            "trade_type": "spot",
            "asset_class": "rwa",
            "venue": "manual_counterparty",
            "quantity": 5000.0,
            "cost_basis_usd": 5250.0,
            "notes": "E2E Test Treasury Allocation for 0x8074...2cAb"
        }
        deal_res = await client.post(f"/api/v1/blotter/{TEST_WALLET}/deals", json=deal_payload)
        print(f"Status: {deal_res.status_code}", flush=True)
        deal_data = deal_res.json()
        deal_id = deal_data.get("id")
        print(f"Created Deal ID: {deal_id}", flush=True)
        print(f"Deal Summary: {deal_data.get('side')} {deal_data.get('quantity')} {deal_data.get('asset_name')} @ ${deal_data.get('cost_basis_usd')}\n", flush=True)
        assert deal_res.status_code == 201

        # 4b. Chainlink Proof of Reserve (PoR) Verification for RWA
        print("--- [STEP 4b: GET /api/v1/blotter/rwa-verification/ONDO_USDY] ---", flush=True)
        rwa_res = await client.get("/api/v1/blotter/rwa-verification/ONDO_USDY")
        print(f"Status: {rwa_res.status_code}", flush=True)
        rwa_data = rwa_res.json()
        print(f"RWA Verified: {rwa_data.get('verified')} | Oracle: {rwa_data.get('oracle_standard')} | Reserve Ratio: {rwa_data.get('reserve_ratio'):.4f}\n", flush=True)
        assert rwa_res.status_code == 200
        assert rwa_data.get("verified") is True

        # 5. Verify Consolidated Portfolio includes both on-chain + manual deals
        print(f"--- [STEP 5: GET /api/v1/portfolio/{TEST_WALLET} (Consolidated Check)] ---", flush=True)
        port_res2 = await client.get(f"/api/v1/portfolio/{TEST_WALLET}")
        port_data2 = port_res2.json()
        print(f"Updated Total Value USD: ${port_data2.get('total_value_usd', 0):,.2f}", flush=True)
        print(f"Total Combined Positions: {len(port_data2.get('positions', []))}", flush=True)
        
        # Verify manual deal exists in consolidated portfolio
        has_manual = any(p["source_type"] == "manual_entry" for p in port_data2.get("positions", []))
        print(f"Manual deal reflected in portfolio: {has_manual}", flush=True)
        assert has_manual is True
        print(flush=True)

        # 6. Portfolio Risk Analytics Endpoint
        print("--- [STEP 6: POST /api/v1/risk/portfolio] ---", flush=True)
        risk_payload = {
            "wallet_address": TEST_WALLET,
            "lookback_days": 30
        }
        risk_res = await client.post("/api/v1/risk/portfolio", json=risk_payload)
        print(f"Status: {risk_res.status_code}", flush=True)
        risk_data = risk_res.json()
        print(f"Net Delta: {risk_data.get('net_delta'):,.2f}", flush=True)
        print(f"Net Gamma: {risk_data.get('net_gamma'):,.4f}", flush=True)
        print(f"Net Vega: {risk_data.get('net_vega'):,.4f}", flush=True)
        print(f"Sharpe Ratio: {risk_data.get('sharpe_ratio'):.4f}", flush=True)
        print(f"Treynor Ratio: {risk_data.get('treynor_ratio'):.4f}", flush=True)
        print(f"Assets in matrix: {risk_data.get('assets')}", flush=True)
        cov = risk_data.get('covariance_matrix', [])
        print(f"Covariance Matrix shape: {len(cov)}x{len(cov[0]) if cov else 0}\n", flush=True)
        assert risk_res.status_code == 200

        # 7. Single Asset Risk Endpoint (for ETH and VIRTUAL)
        for sym in ["ETH", "VIRTUAL"]:
            print(f"--- [STEP 7: POST /api/v1/risk/single for {sym}] ---", flush=True)
            single_res = await client.post("/api/v1/risk/single", json={"asset_id": sym, "lookback_days": 30})
            print(f"Status: {single_res.status_code}", flush=True)
            single_data = single_res.json()
            print(f"Asset: {single_data.get('asset_id')}", flush=True)
            print(f"Beta vs BTC: {single_data.get('beta'):.4f}", flush=True)
            print(f"Annualized Vol: {single_data.get('volatility_annualized', 0) * 100:.2f}%", flush=True)
            print(f"Daily Std Dev: {single_data.get('standard_deviation', 0) * 100:.2f}%", flush=True)
            print(f"Sharpe: {single_data.get('sharpe_ratio'):.4f}", flush=True)
            print(f"Treynor: {single_data.get('treynor_ratio'):.4f}\n", flush=True)
            assert single_res.status_code == 200

        # 8. Institutional Risk Report Endpoint (VaR & CVaR)
        print("--- [STEP 8: POST /api/v1/risk/report] ---", flush=True)
        report_res = await client.post("/api/v1/risk/report", json={"wallet_address": TEST_WALLET})
        print(f"Status: {report_res.status_code}", flush=True)
        report_data = report_res.json()
        print(f"Report ID: {report_data.get('report_id')}", flush=True)
        print(f"1-Day 95% VaR: ${report_data.get('var_95_usd', 0):,.2f}", flush=True)
        print(f"1-Day 99% VaR: ${report_data.get('var_99_usd', 0):,.2f}", flush=True)
        print(f"1-Day 95% Expected Shortfall (CVaR): ${report_data.get('es_95_usd', 0):,.2f}", flush=True)
        print(f"1-Day 99% Expected Shortfall (CVaR): ${report_data.get('es_99_usd', 0):,.2f}", flush=True)
        print(f"Actionable Rebalancing Suggestions ({len(report_data.get('rebalancing_suggestions', []))} items):", flush=True)
        for s in report_data.get("rebalancing_suggestions", []):
            print(f"  * [{s['action_type'].upper()}] {s['asset_id']} Target Delta: ${s['target_delta_usd']:,.2f} | Venue: {s['recommended_venue']}", flush=True)
            print(f"    Rationale: {s['rationale']}", flush=True)
        print(flush=True)
        assert report_res.status_code == 200

        # 9. Non-Custodial Rebalance Swap Quote
        print("--- [STEP 9: POST /api/v1/rebalance/quote] ---", flush=True)
        rebal_payload = {
            "chain_id": 8453,
            "from_token": "ETH",
            "to_token": "USDC",
            "amount": "0.002",
            "venue": "1inch"
        }
        rebal_res = await client.post("/api/v1/rebalance/quote", json=rebal_payload)
        print(f"Status: {rebal_res.status_code}", flush=True)
        rebal_data = rebal_res.json()
        print(f"Venue: {rebal_data.get('venue')}", flush=True)
        print(f"From Amount: {rebal_data.get('from_amount')} ETH -> To Amount: {rebal_data.get('to_amount')} USDC", flush=True)
        print(f"Est Slippage Bps: {rebal_data.get('estimated_slippage_bps')}", flush=True)
        print(f"Est Gas USD: ${rebal_data.get('gas_estimate_usd')}", flush=True)
        print(f"Unsigned Tx Target: {rebal_data.get('unsigned_tx', {}).get('to')}", flush=True)
        print(f"Unsigned Tx Calldata: {rebal_data.get('unsigned_tx', {}).get('data', '')[:42]}...\n", flush=True)
        assert rebal_res.status_code == 200

        # 10. AI Copilot Chat Endpoint
        print("--- [STEP 10: POST /api/v1/copilot/chat] ---", flush=True)
        copilot_payload = {
            "wallet_address": TEST_WALLET,
            "message": "Analyze my portfolio risk metrics, VaR, and recommend hedging steps."
        }
        copilot_res = await client.post("/api/v1/copilot/chat", json=copilot_payload)
        print(f"Status: {copilot_res.status_code}", flush=True)
        copilot_data = copilot_res.json()
        print(f"Copilot Response:\n{copilot_data.get('response_text')}\n", flush=True)
        assert copilot_res.status_code == 200

        # 11. Cleanup test deal
        if deal_id:
            print(f"--- [STEP 11: Cleanup test deal {deal_id}] ---", flush=True)
            del_res = await client.delete(f"/api/v1/blotter/{TEST_WALLET}/deals/{deal_id}")
            print(f"Delete Status: {del_res.status_code}\n", flush=True)
            assert del_res.status_code == 200

    print("============================================================", flush=True)
    print(" ALL END-TO-END TESTS PASSED SUCCESSFULLY FOR WALLET:", flush=True)
    print(f" {TEST_WALLET}", flush=True)
    print("============================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_e2e_testing())
