"use client";

import React, { useState, useEffect } from "react";
import { X, Activity, Info, TrendingUp, ShieldAlert, Cpu } from "lucide-react";

interface Props {
  assetId: string;
  assetName: string;
  onClose: () => void;
}

export function SingleRiskDrawer({ assetId, assetName, onClose }: Props) {
  const [metrics, setMetrics] = useState<any>(null);
  const [lookbackDays, setLookbackDays] = useState(90);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch("/api/v1/risk/single", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ asset_id: assetId, lookback_days: lookbackDays }),
    })
      .then((res) => res.json())
      .then((data) => setMetrics(data))
      .catch((err) => console.error("Error fetching single risk:", err))
      .finally(() => setLoading(false));
  }, [assetId, lookbackDays]);

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      backgroundColor: "rgba(0, 0, 0, 0.65)",
      backdropFilter: "blur(6px)",
      display: "flex",
      justifyContent: "flex-end",
      zIndex: 1000,
    }}>
      <div className="glass-card" style={{
        width: "100%",
        maxWidth: "480px",
        height: "100%",
        padding: "28px",
        borderRadius: "0",
        borderLeft: "1px solid var(--border-subtle)",
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
        gap: "20px"
      }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span className="badge badge-neutral" style={{ textTransform: "uppercase" }}>Single Position Analytics</span>
              <span className="badge badge-positive">BTC Reference Index</span>
            </div>
            <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.6rem", fontWeight: 800 }}>
              {assetName} ({assetId})
            </h2>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer" }}>
            <X size={20} />
          </button>
        </div>

        {/* Lookback Window Selector */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", background: "var(--bg-glass)", padding: "8px 12px", borderRadius: "var(--radius-sm)" }}>
          <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Calculation Horizon:</span>
          {[30, 90, 180, 365].map((d) => (
            <button
              key={d}
              onClick={() => setLookbackDays(d)}
              style={{
                background: lookbackDays === d ? "var(--accent-primary)" : "transparent",
                color: lookbackDays === d ? "#fff" : "var(--text-secondary)",
                border: "none",
                borderRadius: "4px",
                padding: "2px 8px",
                fontSize: "0.75rem",
                cursor: "pointer"
              }}
            >
              {d}d
            </button>
          ))}
        </div>

        {loading || !metrics ? (
          <div style={{ padding: "60px 0", textAlign: "center", color: "var(--text-muted)" }}>
            <Activity className="animate-spin" style={{ margin: "0 auto 12px auto" }} />
            Computing quantitative factor exposures...
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Beta Card */}
            <div className="glass-card" style={{ padding: "16px", borderLeft: "4px solid var(--accent-primary)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Systematic Risk (Beta vs. BTC)</span>
                <span className="badge badge-neutral mono-num">β = {metrics.beta}</span>
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700 }} className="mono-num">
                {metrics.beta}x
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
                {metrics.beta > 1.0 
                  ? "High volatility relative to BTC; amplifies broader crypto market shocks."
                  : metrics.beta > 0.0
                  ? "Defensive sensitivity; returns fluctuate less than the Bitcoin market index."
                  : "Inverse correlation; provides natural portfolio hedging."}
              </p>
            </div>

            {/* Grid for Delta, Volatility, StdDev */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div className="glass-card" style={{ padding: "14px" }}>
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>Directional Delta (Δ)</div>
                <div style={{ fontSize: "1.3rem", fontWeight: 700, marginTop: "4px" }} className="mono-num">
                  {metrics.delta > 0 ? `+${metrics.delta}` : metrics.delta}
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "2px" }}>Linear price sensitivity</div>
              </div>

              <div className="glass-card" style={{ padding: "14px" }}>
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>Annualized Volatility (σ)</div>
                <div style={{ fontSize: "1.3rem", fontWeight: 700, marginTop: "4px", color: "var(--status-warning)" }} className="mono-num">
                  {(metrics.volatility_annualized * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "2px" }}>Annual return dispersion</div>
              </div>

              <div className="glass-card" style={{ padding: "14px" }}>
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>Sharpe Ratio (Rf=0)</div>
                <div style={{ fontSize: "1.3rem", fontWeight: 700, marginTop: "4px", color: metrics.sharpe_ratio >= 1.0 ? "var(--status-positive)" : "var(--text-primary)" }} className="mono-num">
                  {metrics.sharpe_ratio.toFixed(2)}
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "2px" }}>Return per unit total risk</div>
              </div>

              <div className="glass-card" style={{ padding: "14px" }}>
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>Treynor Ratio (Rf=0)</div>
                <div style={{ fontSize: "1.3rem", fontWeight: 700, marginTop: "4px" }} className="mono-num">
                  {metrics.treynor_ratio.toFixed(2)}
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "2px" }}>Return per unit systematic Beta</div>
              </div>
            </div>

            {/* Mathematical Formulas Transparency */}
            <div style={{ background: "rgba(0, 0, 0, 0.3)", padding: "14px", borderRadius: "var(--radius-sm)", fontSize: "0.75rem", color: "var(--text-muted)" }}>
              <div style={{ fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px", display: "flex", alignItems: "center", gap: "6px" }}>
                <Cpu size={12} color="var(--accent-secondary)" /> Deterministic Math Engine
              </div>
              <div>• <strong>Beta Formula:</strong> Cov(R_asset, R_btc) / Var(R_btc)</div>
              <div>• <strong>Sharpe Ratio:</strong> (E[R] - Rf) / σ (annualized with Rf = 0%)</div>
              <div>• <strong>Treynor Ratio:</strong> (E[R_annual] - Rf) / β</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
