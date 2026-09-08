"use client";

import React, { useState, useEffect } from "react";
import { useActiveWallet } from "@/context/WalletContext";
import { PlusCircle, BookOpen, Wallet } from "lucide-react";
import { BlotterTable, DealItem } from "@/components/blotter/BlotterTable";
import { DealEntryModal } from "@/components/blotter/DealEntryModal";
import { usePrivy } from "@privy-io/react-auth";

export default function BlotterPage() {
  const { login } = usePrivy();
  const { activeAddress } = useActiveWallet();

  const [deals, setDeals] = useState<DealItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchDeals = () => {
    if (!activeAddress) {
      setDeals([]);
      return;
    }
    setLoading(true);
    fetch(`http://localhost:8000/api/v1/blotter/${activeAddress}/deals`)
      .then((res) => res.json())
      .then((data) => {
        setDeals(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        console.error("Error fetching deals:", err);
        setDeals([]);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDeals();
  }, [activeAddress]);

  const handleDelete = async (dealId: string) => {
    if (!activeAddress) return;
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

  if (!activeAddress) {
    return (
      <div className="glass-card" style={{ padding: "48px 32px", textAlign: "center", maxWidth: "600px", margin: "40px auto" }}>
        <BookOpen size={36} color="var(--accent-secondary)" style={{ margin: "0 auto 16px auto" }} />
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.5rem", fontWeight: 700, marginBottom: "12px" }}>
          Trade Blotter
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "24px" }}>
          Connect your wallet or enter a public address to view or log OTC deals, centralized exchange positions, and tokenized real-world assets.
        </p>
        <button onClick={login} className="btn btn-primary" style={{ padding: "10px 24px" }}>
          <Wallet size={16} /> Connect Wallet
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header & New Deal Button */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: "1.75rem", fontWeight: 800, marginBottom: "4px" }}>
            Off-Chain & OTC Trade Blotter
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Manual position entries for CEX holdings, OTC deals, Tokenized RWAs, and Perpetual futures
          </p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="btn btn-primary" style={{ gap: "8px" }}>
          <PlusCircle size={16} />
          Log Manual Deal
        </button>
      </div>

      {/* Blotter Data Table */}
      <BlotterTable deals={deals} onDeleteDeal={handleDelete} />

      {/* Deal Entry Modal */}
      {isModalOpen && (
        <DealEntryModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSuccess={handleDealCreated}
          walletAddress={activeAddress}
        />
      )}
    </div>
  );
}
