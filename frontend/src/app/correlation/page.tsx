"use client";

import React, { useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { CovarianceMatrix } from "@/components/risk/CovarianceMatrix";
import { NetGreeksCards } from "@/components/dashboard/NetGreeksCards";
import { Layers, Activity } from "lucide-react";

export default function CorrelationPage() {
  const { authenticated, user } = usePrivy();
  const activeAddress = authenticated && user?.wallet?.address 
    ? user.wallet.address 
    : "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045";

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/api/v1/risk/portfolio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ wallet_address: activeAddress, lookback_days: 90 }),
    })
      .then((res) => res.json())
      .then((resData) => setData(resData))
      .catch((err) => console.error("Error fetching correlation data:", err))
      .finally(() => setLoading(false));
  }, [activeAddress]);

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontFamily: "var(--font-display)", fontSize: "2rem", fontWeight: 800 }}>
          Portfolio Greek & Correlation Analytics
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
          Full high-dimensional Variance-Covariance matrix (Σ) and aggregate Net Greek exposures
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
