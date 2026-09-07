"use client";

import React, { useState } from "react";
import { AlertCircle, X, ShieldCheck } from "lucide-react";

export function ProvenanceAlert() {
  const [visible, setVisible] = useState(true);

  if (!visible) return null;

  return (
    <div style={{
      background: "rgba(6, 182, 212, 0.08)",
      borderBottom: "1px solid rgba(6, 182, 212, 0.2)",
      padding: "8px 24px",
      fontSize: "0.8rem",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      color: "var(--accent-secondary)"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <ShieldCheck size={14} />
        <span>
          <strong>Data Provenance Active:</strong> Real-time pricing anchored to Chainlink oracles; tokenized RWAs verified via Chainlink Proof of Reserve (PoR). Graceful degradation with fallback oracles enabled.
        </span>
      </div>
      <button onClick={() => setVisible(false)} style={{ background: "none", border: "none", color: "var(--accent-secondary)", cursor: "pointer" }}>
        <X size={14} />
      </button>
    </div>
  );
}
