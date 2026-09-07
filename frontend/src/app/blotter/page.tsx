"use client";

import React, { useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { PlusCircle, BookOpen, Layers } from "lucide-react";
import { BlotterTable, DealItem } from "@/components/blotter/BlotterTable";
import { DealEntryModal } from "@/components/blotter/DealEntryModal";

export default function BlotterPage() {
  const { authenticated, user } = usePrivy();
  const activeAddress = authenticated && user?.wallet?.address 
    ? user.wallet.address 
    : "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045";

  const [deals, setDeals] = useState<DealItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchDeals = () => {
    setLoading(true);
    fetch(`http://localhost:8000/api/v1/blotter/${activeAddress}/deals`)
      .then((res) => res.json())
      .then((data) => {
        setDeals(Array.isArray(data) ? data : []);
      })
      .catch((err) => console.error("Error fetching deals:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDeals();
  }, [activeAddress]);

  const handleDelete = async (dealId: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/blotter/${activeAddress}/deals/${dealId}`, {
        method: "DELETE",
      });
      fetchDeals();
      window.dispatchEvent(new Event("portfolio-updated"));
    } catch (e) {
      console.error("Delete failed:", e);
    }
  };

  const handleDealCreated = () => {
    fetchDeals();
    window.dispatchEvent(new Event("portfolio-updated"));
  };

  return (
    <div>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "16px",
        marginBottom: "24px"
      }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: "2rem", fontWeight: 800 }}>
            Multi-Asset Trade Blotter
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Track off-chain CEX trades, OTC contracts, Tokenized RWAs, and Perpetual futures
          </p>
        </div>

        <button onClick={() => setIsModalOpen(true)} className="btn btn-primary" style={{ gap: "8px" }}>
          <PlusCircle size={16} />
          Record New Position
        </button>
      </div>

      <div className="glass-card" style={{ padding: "16px 20px", marginBottom: "20px", display: "flex", alignItems: "center", gap: "12px", borderLeft: "4px solid var(--accent-primary)" }}>
        <Layers size={20} color="var(--accent-secondary)" />
        <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
          <strong style={{ color: "var(--text-primary)" }}>Portfolio Blending Engine Active:</strong> All recorded deals here are automatically priced, aggregated with your on-chain wallet tokens, and modeled in the whole-portfolio Greeks and Covariance Matrix.
        </div>
      </div>

      <BlotterTable
        deals={deals}
        onDeleteDeal={handleDelete}
        walletAddress={activeAddress}
      />

      <DealEntryModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onDealCreated={handleDealCreated}
        walletAddress={activeAddress}
      />
    </div>
  );
}
