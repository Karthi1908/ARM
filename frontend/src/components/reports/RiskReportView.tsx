"use client";

import React from "react";
import { ShieldAlert, AlertTriangle, ArrowRight, ArrowDownRight, Compass, CheckCircle2 } from "lucide-react";

interface RebalanceActionItem {
  action_type: "trim" | "accumulate" | "hedge";
  asset_id: string;
  target_delta_usd: number;
  rationale: string;
  recommended_venue: string;
}

interface RiskReportData {
  report_id: string;
  timestamp: string;
  var_95_usd: number;
  var_99_usd: number;
  es_95_usd: number;
  es_99_usd: number;
  rebalancing_suggestions: RebalanceActionItem[];
}

interface Props {
  report: RiskReportData;
  onSelectRebalanceAction: (action: RebalanceActionItem) => void;
}

export function RiskReportView({ report, onSelectRebalanceAction }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Executive Tail Risk Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px" }}>
        <div className="glass-card" style={{ padding: "20px", borderLeft: "4px solid var(--status-negative)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>1-Day Value at Risk (95% VaR)</span>
            <span className="badge badge-negative">95% Conf</span>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--status-negative)" }} className="mono-num">
            ${report.var_95_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            Maximum predicted loss over a 24-hour window under 95% of market conditions.
          </p>
        </div>

        <div className="glass-card" style={{ padding: "20px", borderLeft: "4px solid #e11d48" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>1-Day Value at Risk (99% VaR)</span>
            <span className="badge badge-negative">99% Conf</span>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "#e11d48" }} className="mono-num">
            ${report.var_99_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            Extreme shock threshold; losses exceed this value on only 1 out of 100 days.
          </p>
        </div>

        <div className="glass-card" style={{ padding: "20px", borderLeft: "4px solid var(--status-warning)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Expected Shortfall (95% CVaR)</span>
            <span className="badge" style={{ background: "rgba(245, 158, 11, 0.15)", color: "var(--status-warning)" }}>95% ES</span>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--status-warning)" }} className="mono-num">
            ${report.es_95_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            Average expected loss when tail events breach the 95% VaR boundary.
          </p>
        </div>

        <div className="glass-card" style={{ padding: "20px", borderLeft: "4px solid var(--accent-secondary)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Expected Shortfall (99% CVaR)</span>
            <span className="badge" style={{ background: "rgba(6, 182, 212, 0.15)", color: "var(--accent-secondary)" }}>99% ES</span>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--accent-secondary)" }} className="mono-num">
            ${report.es_99_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            Severe tail expectation under black-swan liquidity conditions.
          </p>
        </div>
      </div>

      {/* Actionable Rebalancing Section */}
      <div className="glass-card" style={{ padding: "24px" }}>
        <div style={{ marginBottom: "16px" }}>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.3rem", fontWeight: 700 }}>
            Algorithmic Rebalancing Proposals
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
            Mathematically optimized route suggestions to reduce concentration and lower portfolio VaR
          </p>
        </div>

        {report.rebalancing_suggestions.length === 0 ? (
          <div style={{ padding: "30px", textAlign: "center", color: "var(--status-positive)" }}>
            <CheckCircle2 size={32} style={{ margin: "0 auto 8px auto" }} />
            Your portfolio is currently well-balanced across asset classes. No urgent rebalance required.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {report.rebalancing_suggestions.map((s, idx) => (
              <div
                key={idx}
                style={{
                  background: "var(--bg-glass)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "var(--radius-md)",
                  padding: "18px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  flexWrap: "wrap",
                  gap: "16px"
                }}
              >
                <div style={{ flex: 1, minWidth: "280px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                    <span className={`badge ${s.action_type === "trim" ? "badge-negative" : "badge-positive"}`} style={{ textTransform: "uppercase" }}>
                      {s.action_type}
                    </span>
                    <strong style={{ fontSize: "1.05rem" }}>{s.asset_id}</strong>
                    <span className="mono-num" style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>
                      Target: {s.target_delta_usd < 0 ? `-$${Math.abs(s.target_delta_usd).toLocaleString()}` : `+$${s.target_delta_usd.toLocaleString()}`}
                    </span>
                    <span className="badge badge-neutral">Route: {s.recommended_venue.toUpperCase()}</span>
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                    {s.rationale}
                  </p>
                </div>

                <div>
                  <button
                    onClick={() => onSelectRebalanceAction(s)}
                    className="btn btn-primary"
                    style={{ gap: "6px", fontSize: "0.85rem" }}
                  >
                    Simulate Swap Route <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: "16px", padding: "12px", background: "rgba(99, 102, 241, 0.08)", borderRadius: "var(--radius-sm)", fontSize: "0.75rem", color: "var(--text-muted)" }}>
          🔒 <strong>Non-Custodial Constitutional Protection:</strong> The application will NEVER execute or sign trades automatically. Clicking "Simulate Swap Route" fetches a read-only quote; execution requires your interactive wallet signature.
        </div>
      </div>
    </div>
  );
}
