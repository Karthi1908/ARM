"use client";

import React, { useState, useEffect } from "react";
import { X, ArrowRight, ShieldCheck, AlertTriangle, Check, RefreshCw } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  action: {
    action_type: string;
    asset_id: string;
    target_delta_usd: number;
    rationale: string;
    recommended_venue: string;
  } | null;
  walletAddress?: string;
}

export function RebalanceModal({ isOpen, onClose, action, walletAddress }: Props) {
  const [quote, setQuote] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [executedTxHash, setExecutedTxHash] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && action) {
      setLoading(true);
      setExecutedTxHash(null);
      fetch("http://localhost:8000/api/v1/rebalance/quote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chain_id: 1,
          from_token: action.action_type === "trim" ? action.asset_id : "USDC",
          to_token: action.action_type === "trim" ? "ONDO_USDY" : action.asset_id,
          amount: Math.abs(action.target_delta_usd / 3550).toFixed(4), // Approximate token amount
          venue: action.recommended_venue || "1inch",
        }),
      })
        .then((res) => res.json())
        .then((data) => setQuote(data))
        .catch((err) => console.error("Error fetching quote:", err))
        .finally(() => setLoading(false));
    }
  }, [isOpen, action]);

  if (!isOpen || !action) return null;

  const handleSignTransaction = () => {
    setExecuting(true);
    // Simulate user interactive wallet approval & signing
    setTimeout(() => {
      setExecuting(false);
      setExecutedTxHash("0x8f7d9283e1c74829ad30e4299b82173491f9b364810283c7491d904712a839e1");
    }, 1200);
  };

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      backgroundColor: "rgba(0, 0, 0, 0.75)",
      backdropFilter: "blur(8px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1100,
      padding: "20px"
    }}>
      <div className="glass-card" style={{ width: "100%", maxWidth: "550px", padding: "28px", borderRadius: "var(--radius-lg)" }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
              <span className="badge badge-positive">Pre-Flight Simulation</span>
              <span className="badge badge-neutral">{action.recommended_venue.toUpperCase()} Fusion</span>
            </div>
            <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.3rem", fontWeight: 700 }}>
              Confirm Rebalancing Route
            </h3>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer" }}>
            <X size={20} />
          </button>
        </div>

        {loading ? (
          <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
            <RefreshCw className="animate-spin" size={24} style={{ margin: "0 auto 12px auto" }} />
            Fetching executable swap quote and routing calldata...
          </div>
        ) : executedTxHash ? (
          <div style={{ textAlign: "center", padding: "24px 0" }}>
            <div style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              background: "var(--status-positive-bg)",
              color: "var(--status-positive)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 16px auto"
            }}>
              <Check size={32} />
            </div>
            <h4 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "8px" }}>
              Transaction Signed & Broadcast
            </h4>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "16px" }}>
              The rebalancing transaction was successfully signed in your wallet and submitted to the network.
            </p>
            <div className="badge badge-neutral mono-num" style={{ padding: "8px 12px", wordBreak: "break-all" }}>
              Tx: {executedTxHash}
            </div>
            <div style={{ marginTop: "24px" }}>
              <button onClick={onClose} className="btn btn-primary" style={{ width: "100%" }}>
                Done
              </button>
            </div>
          </div>
        ) : (
          <div>
            {/* Swap Summary */}
            <div style={{
              background: "var(--bg-glass)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)",
              padding: "16px",
              marginBottom: "18px"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>You Swap</div>
                  <div style={{ fontSize: "1.2rem", fontWeight: 700 }}>
                    {quote?.from_amount} {quote?.from_token}
                  </div>
                </div>
                <ArrowRight size={20} color="var(--accent-primary)" />
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>You Receive (Est.)</div>
                  <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--status-positive)" }}>
                    {quote?.to_amount} {quote?.to_token}
                  </div>
                </div>
              </div>

              <div style={{ borderTop: "1px solid rgba(255, 255, 255, 0.05)", paddingTop: "10px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "0.8rem" }}>
                <div>
                  <span style={{ color: "var(--text-secondary)" }}>Est. Slippage:</span>{" "}
                  <span className="mono-num">{(quote?.estimated_slippage_bps / 100).toFixed(2)}%</span>
                </div>
                <div style={{ textAlign: "right" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Est. Network Gas:</span>{" "}
                  <span className="mono-num">${quote?.gas_estimate_usd}</span>
                </div>
              </div>
            </div>

            {/* Guardrail Warning */}
            <div style={{
              background: "rgba(245, 158, 11, 0.08)",
              border: "1px solid rgba(245, 158, 11, 0.2)",
              borderRadius: "var(--radius-sm)",
              padding: "12px",
              fontSize: "0.8rem",
              color: "var(--text-secondary)",
              display: "flex",
              alignItems: "flex-start",
              gap: "8px",
              marginBottom: "20px"
            }}>
              <AlertTriangle size={16} color="var(--status-warning)" style={{ flexShrink: 0, marginTop: "2px" }} />
              <div>
                <strong>Explicit User Consent Gate:</strong> This action will trigger a signature prompt in your connected wallet. The Agentic Risk Manager cannot sign or broadcast transactions on your behalf.
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
              <button onClick={onClose} className="btn btn-secondary">
                Cancel
              </button>
              <button
                onClick={handleSignTransaction}
                disabled={executing}
                className="btn btn-primary"
                style={{ gap: "6px" }}
              >
                <ShieldCheck size={16} />
                {executing ? "Requesting Wallet Signature..." : "Sign in Wallet to Execute"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
