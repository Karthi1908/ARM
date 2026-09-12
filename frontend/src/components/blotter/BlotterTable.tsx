"use client";

import React, { useState, useEffect } from "react";
import { Trash2, ShieldCheck, HelpCircle, Filter } from "lucide-react";

export interface DealItem {
  id: string;
  asset_name: string;
  trade_date: string;
  side: "buy" | "sell";
  trade_type: string;
  asset_class: "crypto" | "rwa" | "perpetual";
  settlement_date?: string | null;
  venue: string;
  quantity: number;
  cost_basis_usd: number;
  notes?: string | null;
}

interface Props {
  deals: DealItem[];
  onDeleteDeal: (id: string) => void;
  walletAddress: string;
}

export function BlotterTable({ deals, onDeleteDeal, walletAddress }: Props) {
  const [filterClass, setFilterClass] = useState<string>("all");
  const [rwaVerifications, setRwaVerifications] = useState<Record<string, any>>({});
  const [riskMetrics, setRiskMetrics] = useState<Record<string, { beta: number; sharpe: number; treynor: number }>>({});

  useEffect(() => {
    // Check RWA verification for unique RWA assets
    const rwaAssets = Array.from(new Set(deals.filter(d => d.asset_class === "rwa").map(d => d.asset_name)));
    rwaAssets.forEach(async (symbol) => {
      try {
        const res = await fetch(`/api/v1/blotter/rwa-verification/${symbol}`);
        if (res.ok) {
          const data = await res.json();
          setRwaVerifications(prev => ({ ...prev, [symbol]: data }));
        }
      } catch {}
    });

    // Resolve single risk metrics for all unique deal assets
    const uniqueAssets = Array.from(new Set(deals.map(d => d.asset_name.toUpperCase()))).filter(
      sym => !riskMetrics[sym]
    );

    uniqueAssets.forEach(async (sym) => {
      try {
        const res = await fetch("/api/v1/risk/single", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ asset_id: sym, lookback_days: 90 }),
        });
        if (res.ok) {
          const data = await res.json();
          setRiskMetrics(prev => ({
            ...prev,
            [sym]: {
              beta: data.beta,
              sharpe: data.sharpe_ratio,
              treynor: data.treynor_ratio,
            },
          }));
        }
      } catch {}
    });
  }, [deals]);

  const filteredDeals = deals.filter(d => filterClass === "all" || d.asset_class === filterClass);

  return (
    <div className="glass-card" style={{ padding: "20px" }}>
      {/* Filter Toolbar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Filter size={16} color="var(--text-secondary)" />
          <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Filter Asset Class:</span>
          {["all", "crypto", "rwa", "perpetual"].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterClass(cat)}
              className="btn btn-secondary"
              style={{
                padding: "4px 10px",
                fontSize: "0.75rem",
                textTransform: "capitalize",
                background: filterClass === cat ? "rgba(99, 102, 241, 0.2)" : "transparent",
                borderColor: filterClass === cat ? "var(--accent-primary)" : "var(--border-subtle)",
              }}
            >
              {cat}
            </button>
          ))}
        </div>
        <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
          Showing {filteredDeals.length} of {deals.length} recorded deals
        </div>
      </div>

      {/* Table */}
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)", fontSize: "0.8rem", textTransform: "uppercase" }}>
              <th style={{ padding: "12px 14px" }}>Date</th>
              <th style={{ padding: "12px 14px" }}>Asset</th>
              <th style={{ padding: "12px 14px" }}>Class</th>
              <th style={{ padding: "12px 14px" }}>Side</th>
              <th style={{ padding: "12px 14px" }}>Type</th>
              <th style={{ padding: "12px 14px" }}>Venue</th>
              <th style={{ padding: "12px 14px", textAlign: "right" }}>Quantity</th>
              <th style={{ padding: "12px 14px", textAlign: "right" }}>Cost Basis</th>
              <th style={{ padding: "12px 14px", textAlign: "right" }}>Beta (vs BTC)</th>
              <th style={{ padding: "12px 14px", textAlign: "right" }}>Sharpe (Rf=0)</th>
              <th style={{ padding: "12px 14px", textAlign: "right" }}>Treynor</th>
              <th style={{ padding: "12px 14px" }}>Settlement</th>
              <th style={{ padding: "12px 14px", textAlign: "center" }}>PoR Status</th>
              <th style={{ padding: "12px 14px", textAlign: "center" }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredDeals.length === 0 ? (
              <tr>
                <td colSpan={14} style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
                  No manual deals match the selected criteria.
                </td>
              </tr>
            ) : (
              filteredDeals.map((deal) => {
                const verification = rwaVerifications[deal.asset_name];
                return (
                  <tr key={deal.id} style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.04)" }}>
                    <td style={{ padding: "12px 14px", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                      {deal.trade_date}
                    </td>
                    <td style={{ padding: "12px 14px", fontWeight: 600 }}>
                      {deal.asset_name}
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <span className="badge badge-neutral" style={{ textTransform: "uppercase" }}>
                        {deal.asset_class}
                      </span>
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <span className={`badge ${deal.side === "buy" ? "badge-positive" : "badge-negative"}`}>
                        {deal.side.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: "12px 14px", fontSize: "0.85rem", textTransform: "capitalize" }}>
                      {deal.trade_type}
                    </td>
                    <td style={{ padding: "12px 14px", fontSize: "0.85rem" }}>
                      {deal.venue}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "right" }} className="mono-num">
                      {deal.quantity.toLocaleString(undefined, { maximumFractionDigits: 4 })}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "right" }} className="mono-num">
                      ${deal.cost_basis_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "right" }} className="mono-num">
                      {riskMetrics[deal.asset_name.toUpperCase()] ? (
                        <span style={{
                          color: riskMetrics[deal.asset_name.toUpperCase()].beta > 1.2
                            ? "var(--status-warning)"
                            : riskMetrics[deal.asset_name.toUpperCase()].beta < 0.5
                            ? "var(--status-positive)"
                            : "var(--text-primary)"
                        }}>
                          {riskMetrics[deal.asset_name.toUpperCase()].beta.toFixed(2)}x
                        </span>
                      ) : (
                        <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>calc...</span>
                      )}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "right" }} className="mono-num">
                      {riskMetrics[deal.asset_name.toUpperCase()] ? (
                        <span style={{
                          color: riskMetrics[deal.asset_name.toUpperCase()].sharpe >= 1.0
                            ? "var(--status-positive)"
                            : "var(--text-primary)"
                        }}>
                          {riskMetrics[deal.asset_name.toUpperCase()].sharpe.toFixed(2)}
                        </span>
                      ) : (
                        <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>calc...</span>
                      )}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "right" }} className="mono-num">
                      {riskMetrics[deal.asset_name.toUpperCase()] ? (
                        <span>
                          {riskMetrics[deal.asset_name.toUpperCase()].treynor.toFixed(2)}
                        </span>
                      ) : (
                        <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>calc...</span>
                      )}
                    </td>
                    <td style={{ padding: "12px 14px", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                      {deal.settlement_date || "N/A (Spot)"}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "center" }}>
                      {deal.asset_class === "rwa" ? (
                        verification?.verified ? (
                          <span className="badge badge-positive" title={`Verified via ${verification.oracle_standard}`}>
                            <ShieldCheck size={12} /> PoR Verified
                          </span>
                        ) : (
                          <span className="badge badge-neutral" title="Unverified RWA">
                            <HelpCircle size={12} /> Unverified
                          </span>
                        )
                      ) : (
                        <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>—</span>
                      )}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "center" }}>
                      <button
                        onClick={() => onDeleteDeal(deal.id)}
                        className="btn btn-secondary"
                        style={{ padding: "6px", color: "var(--status-negative)", borderColor: "rgba(244, 63, 94, 0.2)" }}
                        title="Delete deal"
                      >
                        <Trash2 size={14} />
                      </button>
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
