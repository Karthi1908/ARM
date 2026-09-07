"use client";

import React, { useState } from "react";
import { X, PlusCircle, Check, AlertCircle } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onDealCreated: () => void;
  walletAddress: string;
}

export function DealEntryModal({ isOpen, onClose, onDealCreated, walletAddress }: Props) {
  const [assetName, setAssetName] = useState("");
  const [tradeDate, setTradeDate] = useState(new Date().toISOString().split("T")[0]);
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [tradeType, setTradeType] = useState("spot");
  const [assetClass, setAssetClass] = useState<"crypto" | "rwa" | "perpetual">("crypto");
  const [settlementDate, setSettlementDate] = useState("");
  const [venue, setVenue] = useState("");
  const [quantity, setQuantity] = useState("");
  const [costBasis, setCostBasis] = useState("");
  const [notes, setNotes] = useState("");
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const qty = parseFloat(quantity);
    const cost = parseFloat(costBasis);

    if (!assetName.trim() || !venue.trim()) {
      setError("Please fill out asset name and venue.");
      return;
    }

    if (isNaN(qty) || qty <= 0 || isNaN(cost) || cost <= 0) {
      setError("Quantity and cost basis must be positive numbers.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/blotter/${walletAddress}/deals`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          asset_name: assetName.toUpperCase(),
          trade_date: tradeDate,
          side,
          trade_type: tradeType,
          asset_class: assetClass,
          settlement_date: settlementDate || null,
          venue,
          quantity: qty,
          cost_basis_usd: cost,
          notes: notes || null,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to record deal.");
      }

      onDealCreated();
      onClose();
      // Reset
      setAssetName("");
      setQuantity("");
      setCostBasis("");
      setVenue("");
      setNotes("");
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setSubmitting(false);
    }
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
      zIndex: 1000,
      padding: "20px"
    }}>
      <div className="glass-card" style={{ width: "100%", maxWidth: "600px", padding: "28px", borderRadius: "var(--radius-lg)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <div>
            <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.3rem", fontWeight: 700 }}>
              Record Manual Deal
            </h3>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
              Log CEX trades, OTC contracts, Tokenized RWAs, or Perpetual positions
            </p>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer" }}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div style={{
            background: "var(--status-negative-bg)",
            border: "1px solid var(--status-negative)",
            color: "var(--status-negative)",
            padding: "10px 14px",
            borderRadius: "var(--radius-sm)",
            fontSize: "0.85rem",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            marginBottom: "16px"
          }}>
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Asset Symbol / Name *
              </label>
              <input
                type="text"
                placeholder="e.g. SOL, ONDO_USDY, BTC-PERP"
                value={assetName}
                onChange={(e) => setAssetName(e.target.value)}
                required
                style={{ width: "100%" }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Asset Class *
              </label>
              <select
                value={assetClass}
                onChange={(e) => setAssetClass(e.target.value as any)}
                style={{ width: "100%" }}
              >
                <option value="crypto">Crypto (Spot)</option>
                <option value="rwa">Real-World Asset (RWA)</option>
                <option value="perpetual">Perpetual / Derivative</option>
              </select>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "14px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Side *
              </label>
              <select value={side} onChange={(e) => setSide(e.target.value as any)} style={{ width: "100%" }}>
                <option value="buy">Buy / Long</option>
                <option value="sell">Sell / Short</option>
              </select>
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Trade Type *
              </label>
              <select value={tradeType} onChange={(e) => setTradeType(e.target.value)} style={{ width: "100%" }}>
                <option value="spot">Spot</option>
                <option value="forward">Forward</option>
                <option value="future">Future</option>
                <option value="option_call">Option Call</option>
                <option value="option_put">Option Put</option>
              </select>
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Execution Venue *
              </label>
              <input
                type="text"
                placeholder="e.g. Binance, Ondo, Deribit"
                value={venue}
                onChange={(e) => setVenue(e.target.value)}
                required
                style={{ width: "100%" }}
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Position Quantity *
              </label>
              <input
                type="number"
                step="any"
                placeholder="e.g. 15.5"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
                style={{ width: "100%" }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Unit Cost Basis (USD) *
              </label>
              <input
                type="number"
                step="any"
                placeholder="e.g. 142.50"
                value={costBasis}
                onChange={(e) => setCostBasis(e.target.value)}
                required
                style={{ width: "100%" }}
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Trade Date *
              </label>
              <input
                type="date"
                value={tradeDate}
                onChange={(e) => setTradeDate(e.target.value)}
                required
                style={{ width: "100%" }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
                Settlement Date (Optional)
              </label>
              <input
                type="date"
                value={settlementDate}
                onChange={(e) => setSettlementDate(e.target.value)}
                style={{ width: "100%" }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Deal Notes
            </label>
            <input
              type="text"
              placeholder="e.g. OTC hedge agreement"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              style={{ width: "100%" }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px", marginTop: "10px" }}>
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={submitting} className="btn btn-primary" style={{ gap: "6px" }}>
              <PlusCircle size={16} />
              {submitting ? "Saving Deal..." : "Record Deal"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
