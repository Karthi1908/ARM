"use client";

import React, { useState } from "react";
import { Grid, Eye, Layers } from "lucide-react";

interface Props {
  assets: string[];
  covarianceMatrix: number[][];
  correlationMatrix: number[][];
}

export function CovarianceMatrix({ assets, covarianceMatrix, correlationMatrix }: Props) {
  const [viewType, setViewType] = useState<"correlation" | "covariance">("correlation");
  const matrix = viewType === "correlation" ? correlationMatrix : covarianceMatrix;

  const getHeatmapColor = (val: number, isCorrelation: boolean) => {
    if (!isCorrelation) {
      // Covariance scaling
      return "rgba(99, 102, 241, 0.15)";
    }
    // Correlation between -1.0 and +1.0
    if (val >= 0.8) return "rgba(99, 102, 241, 0.65)"; // Strong positive
    if (val >= 0.4) return "rgba(6, 182, 212, 0.4)";
    if (val >= 0.0) return "rgba(255, 255, 255, 0.05)";
    if (val >= -0.4) return "rgba(245, 158, 11, 0.3)";
    return "rgba(244, 63, 94, 0.5)"; // Strong negative
  };

  if (!assets || assets.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
        Add at least two assets to compute the Variance-Covariance Matrix.
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: "24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "10px" }}>
        <div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.3rem", fontWeight: 700 }}>
            {viewType === "correlation" ? "Asset Correlation Heatmap (ρ)" : "Variance-Covariance Matrix (Σ)"}
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
            {viewType === "correlation" 
              ? "Normalized pairwise return correlations from -1.0 (inverse) to +1.0 (perfectly correlated)"
              : "Annualized asset-to-asset return variances and covariances"}
          </p>
        </div>

        <div style={{ display: "flex", gap: "8px", background: "var(--bg-glass)", padding: "4px", borderRadius: "var(--radius-sm)" }}>
          <button
            onClick={() => setViewType("correlation")}
            className="btn btn-secondary"
            style={{
              padding: "6px 14px",
              fontSize: "0.8rem",
              background: viewType === "correlation" ? "var(--accent-primary)" : "transparent",
              color: viewType === "correlation" ? "#fff" : "var(--text-secondary)",
              border: "none"
            }}
          >
            Correlation Matrix
          </button>
          <button
            onClick={() => setViewType("covariance")}
            className="btn btn-secondary"
            style={{
              padding: "6px 14px",
              fontSize: "0.8rem",
              background: viewType === "covariance" ? "var(--accent-primary)" : "transparent",
              color: viewType === "covariance" ? "#fff" : "var(--text-secondary)",
              border: "none"
            }}
          >
            Covariance Matrix (Σ)
          </button>
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ borderCollapse: "separate", borderSpacing: "4px", width: "100%", textAlign: "center" }}>
          <thead>
            <tr>
              <th style={{ padding: "10px", color: "var(--text-muted)", fontSize: "0.8rem", textAlign: "left" }}>Asset</th>
              {assets.map((a) => (
                <th key={a} style={{ padding: "10px", color: "var(--text-primary)", fontSize: "0.85rem", fontWeight: 600 }}>
                  {a}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {assets.map((rowAsset, i) => (
              <tr key={rowAsset}>
                <td style={{ padding: "10px", fontWeight: 600, fontSize: "0.85rem", textAlign: "left", color: "var(--text-primary)" }}>
                  {rowAsset}
                </td>
                {assets.map((colAsset, j) => {
                  const val = matrix[i] ? matrix[i][j] : 0;
                  const isDiag = i === j;
                  return (
                    <td
                      key={colAsset}
                      style={{
                        padding: "14px 10px",
                        borderRadius: "6px",
                        background: isDiag ? "rgba(99, 102, 241, 0.25)" : getHeatmapColor(val, viewType === "correlation"),
                        border: isDiag ? "1px solid var(--accent-primary)" : "1px solid rgba(255, 255, 255, 0.04)",
                        fontWeight: isDiag ? 700 : 500,
                        fontSize: "0.85rem",
                        transition: "var(--transition)"
                      }}
                      className="mono-num"
                      title={`${rowAsset} vs ${colAsset}: ${val}`}
                    >
                      {viewType === "correlation" ? (val >= 0 ? `+${val.toFixed(2)}` : val.toFixed(2)) : val.toFixed(4)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
