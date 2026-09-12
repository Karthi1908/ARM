"use client";

import React, { useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { useActiveWallet } from "@/context/WalletContext";
import { CovarianceMatrix } from "@/components/risk/CovarianceMatrix";
import { NetGreeksCards } from "@/components/dashboard/NetGreeksCards";
import { Layers, Activity, Wallet } from "lucide-react";

export default function CorrelationPage() {
  const { login } = usePrivy();
  const { activeAddress } = useActiveWallet();

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!activeAddress) {
      setData(null);
      return;
    }
    setLoading(true);
    fetch("/api/v1/risk/portfolio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ wallet_address: activeAddress, lookback_days: 90 }),
    })
      .then((res) => res.json())
      .then((resData) => setData(resData))
      .catch((err) => {
        console.error("Error fetching correlation data:", err);
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [activeAddress]);

  if (!activeAddress) {
    return (
      <div className="glass-card" style={{ padding: "48px 32px", textAlign: "center", maxWidth: "600px", margin: "40px auto" }}>
        <Layers size={36} color="var(--accent-primary)" style={{ margin: "0 auto 16px auto" }} />
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.5rem", fontWeight: 700, marginBottom: "12px" }}>
          Pairwise Correlation Matrix
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "24px" }}>
          Connect your wallet or enter a public address in the header to compute actual covariance and correlation across your live holdings.
        </p>
        <button onClick={login} className="btn btn-primary" style={{ padding: "10px 24px" }}>
          <Wallet size={16} /> Connect Wallet
        </button>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontFamily: "var(--font-display)", fontSize: "2rem", fontWeight: 800 }}>
          Portfolio Greek & Correlation Analytics
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
          Full high-dimensional Variance-Covariance matrix (Σ) and aggregate Net Greek exposures from actual holdings
        </p>
      </div>

      <NetGreeksCards walletAddress={activeAddress} />

      {loading || !data ? (
        <div className="glass-card" style={{ padding: "60px", textAlign: "center", color: "var(--text-muted)" }}>
          <Activity className="animate-spin" size={24} style={{ margin: "0 auto 12px auto" }} />
          Computing pairwise covariance matrix from historical returns...
        </div>
      ) : (
        <CovarianceMatrix
          assets={data.assets || []}
          covarianceMatrix={data.covariance_matrix || []}
          correlationMatrix={data.correlation_matrix || []}
        />
      )}
    </div>
  );
}
