"use client";

import React, { useState, useEffect } from "react";
import { TrendingUp, Layers, ChevronRight, Activity, Percent, BarChart3 } from "lucide-react";

export interface PositionItem {
  id: string;
  asset_id: string;
  symbol: string;
  name: string;
  asset_class: "crypto" | "rwa" | "perpetual";
  source_type: "on_chain_discovered" | "manual_entry";
  chain_id?: number | null;
  quantity: number;
  unit_price_usd: number;
  total_value_usd: number;
}

interface Props {
  positions: PositionItem[];
  onSelectPosition: (pos: PositionItem) => void;
  selectedAssetId?: string | null;
  onHedgePosition?: (pos: PositionItem) => void;
}

export function HoldingsTable({ positions, onSelectPosition, selectedAssetId, onHedgePosition }: Props) {
  const [riskMetrics, setRiskMetrics] = useState<Record<string, { beta: number; sharpe: number; treynor: number }>>({});

  useEffect(() => {
    // Asynchronously resolve single-position risk metrics for priced assets
    const uniqueSymbols = Array.from(new Set(positions.map((p) => p.symbol.toUpperCase()))).filter(
      (sym) => !riskMetrics[sym]
    );

    if (uniqueSymbols.length === 0) return;

    uniqueSymbols.forEach((sym) => {
      fetch("http://localhost:8000/api/v1/risk/single", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asset_id: sym, lookback_days: 90 }),
      })
        .then((res) => res.json())
        .then((data) => {
          setRiskMetrics((prev) => ({
            ...prev,
            [sym]: {
              beta: data.beta,
              sharpe: data.sharpe_ratio,
              treynor: data.treynor_ratio,
            },
          }));
        })
        .catch(() => {});
    });
  }, [positions]);

  const getChainName = (chainId?: number | null) => {
    switch (chainId) {
      case 1: return "Ethereum";
      case 42161: return "Arbitrum";
      case 10: return "Optimism";
      case 8453: return "Base";
      default: return "Multi-Chain / CEX";
    }
  };

  const getAssetClassBadge = (assetClass: string) => {
    switch (assetClass) {
      case "rwa":
        return <span className="badge" style={{ background: "rgba(6, 182, 212, 0.15)", color: "var(--accent-secondary)", border: "1px solid rgba(6, 182, 212, 0.3)" }}>RWA (PoR)</span>;
      case "perpetual":
        return <span className="badge" style={{ background: "rgba(244, 63, 94, 0.15)", color: "var(--status-negative)", border: "1px solid rgba(244, 63, 94, 0.3)" }}>Perpetual</span>;
      default:
        return <span className="badge badge-neutral">Crypto Spot</span>;
    }
  };

  return (
    <div className="glass-card" style={{ padding: "20px", marginTop: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.25rem", fontWeight: 700 }}>
            Unified Portfolio Holdings
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
            Cross-chain discovered tokens and manually logged positions
          </p>
        </div>
        <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
          <Activity size={14} color="var(--accent-secondary)" />
          Click any row to inspect single-deal quantitative risk
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)", fontSize: "0.8rem", textTransform: "uppercase" }}>
              <th style={{ padding: "12px 16px" }}>Asset</th>
              <th style={{ padding: "12px 16px" }}>Class</th>
              <th style={{ padding: "12px 16px" }}>Chain / Source</th>
              <th style={{ padding: "12px 16px", textAlign: "right" }}>Quantity</th>
              <th style={{ padding: "12px 16px", textAlign: "right" }}>Price (USD)</th>
              <th style={{ padding: "12px 16px", textAlign: "right" }}>Total Value</th>
              <th style={{ padding: "12px 16px", textAlign: "right" }}>Beta (vs BTC)</th>
              <th style={{ padding: "12px 16px", textAlign: "right" }}>Sharpe (Rf=0)</th>
              <th style={{ padding: "12px 16px", textAlign: "right" }}>Treynor</th>
              <th style={{ padding: "12px 16px", textAlign: "center" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {positions.length === 0 ? (
              <tr>
                <td colSpan={10} style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
                  No active holdings discovered. Click "Sync" or add a manual deal.
                </td>
              </tr>
            ) : (
              positions.map((pos) => {
                const isSelected = selectedAssetId === pos.asset_id;
                return (
                  <tr
                    key={pos.id}
                    onClick={() => onSelectPosition(pos)}
                    style={{
                      borderBottom: "1px solid rgba(255, 255, 255, 0.04)",
                      cursor: "pointer",
                      transition: "var(--transition)",
                      background: isSelected ? "rgba(99, 102, 241, 0.12)" : "transparent",
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)";
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) e.currentTarget.style.background = "transparent";
                    }}
                  >
                    <td style={{ padding: "14px 16px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <div style={{
                          width: "32px",
                          height: "32px",
                          borderRadius: "50%",
                          background: "var(--bg-glass)",
                          border: "1px solid var(--border-subtle)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontWeight: 700,
                          fontSize: "0.75rem",
                          color: "var(--accent-secondary)"
                        }}>
                          {pos.symbol.slice(0, 3)}
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: "0.95rem" }}>{pos.name}</div>
                          <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>{pos.symbol}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: "14px 16px" }}>{getAssetClassBadge(pos.asset_class)}</td>
                    <td style={{ padding: "14px 16px", color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                      {pos.source_type === "manual_entry" ? "Manual Deal" : getChainName(pos.chain_id)}
                    </td>
                    <td style={{ padding: "14px 16px", textAlign: "right" }} className="mono-num">
                      {pos.quantity.toLocaleString(undefined, { maximumFractionDigits: 4 })}
                    </td>
                    <td style={{ padding: "14px 16px", textAlign: "right" }} className="mono-num">
                      {pos.unit_price_usd > 0 ? (
                        `$${pos.unit_price_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                      ) : (
                        <span style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                          fontSize: "0.75rem",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          background: "rgba(255, 255, 255, 0.05)",
                          color: "var(--text-muted)",
                          border: "1px solid rgba(255, 255, 255, 0.1)"
                        }}>
                          $0.00 <span style={{ fontSize: "0.65rem", opacity: 0.75 }}>Unpriced</span>
                        </span>
                      )}
                    </td>
                    <td style={{ padding: "14px 16px", textAlign: "right", fontWeight: 700 }} className="mono-num">
                      {pos.total_value_usd > 0 ? (
                        `$${pos.total_value_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                      ) : (
                        <span style={{ color: "var(--text-muted)", fontWeight: 500 }}>$0.00</span>
                      )}
                    </td>
                    <td style={{ padding: "14px 16px", textAlign: "right" }} className="mono-num">
                      {pos.unit_price_usd > 0 ? (
                        riskMetrics[pos.symbol.toUpperCase()] ? (
                          <span style={{
                            color: riskMetrics[pos.symbol.toUpperCase()].beta > 1.2
                              ? "var(--status-warning)"
                              : riskMetrics[pos.symbol.toUpperCase()].beta < 0.5
                              ? "var(--status-positive)"
                              : "var(--text-primary)"
                          }}>
                            {riskMetrics[pos.symbol.toUpperCase()].beta.toFixed(2)}x
                          </span>
                        ) : (
                          <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>calc...</span>
                        )
                      ) : (
                        <span style={{ color: "var(--text-muted)" }}>-</span>
                      )}
                    </td>
                    <td style={{ padding: "14px 16px", textAlign: "right" }} className="mono-num">
                      {pos.unit_price_usd > 0 ? (
                        riskMetrics[pos.symbol.toUpperCase()] ? (
                          <span style={{
                            color: riskMetrics[pos.symbol.toUpperCase()].sharpe >= 1.0
                              ? "var(--status-positive)"
                              : "var(--text-primary)"
                          }}>
                            {riskMetrics[pos.symbol.toUpperCase()].sharpe.toFixed(2)}
                          </span>
                        ) : (
                          <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>calc...</span>
                        )
                      ) : (
                        <span style={{ color: "var(--text-muted)" }}>-</span>
                      )}
                    </td>
                    <td style={{ padding: "14px 16px", textAlign: "right" }} className="mono-num">
                      {pos.unit_price_usd > 0 ? (
                        riskMetrics[pos.symbol.toUpperCase()] ? (
                          <span>
                            {riskMetrics[pos.symbol.toUpperCase()].treynor.toFixed(2)}
                          </span>
                        ) : (
                          <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>calc...</span>
                        )
                      ) : (
                        <span style={{ color: "var(--text-muted)" }}>-</span>
                      )}
                    </td>
                    <td style={{ padding: "14px 16px", textAlign: "center" }}>
                      <div style={{ display: "flex", gap: "6px", justifyContent: "center" }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectPosition(pos);
                          }}
                          className="btn btn-secondary"
                          style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                        >
                          Inspect <ChevronRight size={12} />
                        </button>
                        {onHedgePosition && pos.symbol.toUpperCase() !== "USDC" && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onHedgePosition(pos);
                            }}
                            className="btn btn-primary"
                            style={{ padding: "4px 8px", fontSize: "0.75rem", background: "rgba(99, 102, 241, 0.2)", border: "1px solid rgba(99, 102, 241, 0.4)" }}
                            title="Hedge or convert into USDC via Uniswap AI"
                          >
                            Hedge
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
