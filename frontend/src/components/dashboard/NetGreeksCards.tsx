"use client";

import React, { useState, useEffect } from "react";
import { Activity, Zap, Compass, BarChart, Percent } from "lucide-react";

interface Props {
  walletAddress: string;
}

export function NetGreeksCards({ walletAddress }: Props) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchPortfolioRisk = () => {
    setLoading(true);
    fetch("http://localhost:8000/api/v1/risk/portfolio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ wallet_address: walletAddress, lookback_days: 90 }),
    })
      .then((res) => res.json())
      .then((resData) => setData(resData))
      .catch((err) => console.error("Error fetching portfolio Greeks:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPortfolioRisk();
    const handleUpdate = () => fetchPortfolioRisk();
    window.addEventListener("portfolio-updated", handleUpdate);
    return () => window.removeEventListener("portfolio-updated", handleUpdate);
  }, [walletAddress]);

  if (loading || !data) {
    return (
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        {[1, 2, 3, 4, 5].map((n) => (
          <div key={n} className="glass-card" style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
            <Activity className="animate-spin" size={20} style={{ margin: "0 auto 8px auto" }} />
            Computing Net Greeks...
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      label: "Net Portfolio Delta (Δ)",
      value: data.net_delta > 0 ? `+${data.net_delta.toLocaleString()}` : data.net_delta.toLocaleString(),
      subtext: "Aggregate directional market exposure",
      color: "var(--accent-primary)",
      icon: Compass,
    },
    {
      label: "Net Portfolio Vega (ν)",
      value: data.net_vega.toFixed(2),
      subtext: "USD impact per 1% implied vol shift",
      color: "var(--accent-secondary)",
      icon: Zap,
    },
    {
      label: "Net Portfolio Gamma (Γ)",
      value: data.net_gamma.toFixed(6),
      subtext: "Convexity / acceleration of Delta",
      color: "var(--status-warning)",
      icon: Activity,
    },
    {
      label: "Portfolio Sharpe Ratio",
      value: data.sharpe_ratio.toFixed(2),
      subtext: "Annualized excess return (Rf = 0%)",
      color: data.sharpe_ratio >= 1.0 ? "var(--status-positive)" : "var(--text-primary)",
      icon: BarChart,
    },
    {
      label: "Portfolio Treynor Ratio",
      value: data.treynor_ratio.toFixed(2),
      subtext: "Return per unit systematic risk",
      color: "var(--text-primary)",
      icon: Percent,
    },
  ];

  return (
    <div style={{ marginBottom: "20px" }}>
      {data?.math_engine_version && (
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "6px" }}>
          <span className="badge badge-neutral" style={{ fontSize: "0.68rem", display: "inline-flex", alignItems: "center", gap: "4px", color: "var(--text-muted)" }}>
            ⚡ Deterministic Risk Engine: {data.math_engine_version}
          </span>
        </div>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
        {cards.map((c, i) => {
          const Icon = c.icon;
          return (
            <div key={i} className="glass-card" style={{ padding: "20px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontWeight: 500 }}>{c.label}</span>
                <div style={{ padding: "6px", borderRadius: "8px", background: "var(--bg-glass)" }}>
                  <Icon size={16} color={c.color} />
                </div>
              </div>
              <div>
                <div style={{ fontSize: "1.8rem", fontWeight: 800, color: c.color }} className="mono-num">
                  {c.value}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
                  {c.subtext}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
