"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { usePrivy } from "@privy-io/react-auth";
import { Shield, Wallet, RefreshCw, BarChart3, BookOpen, Layers, FileText, CheckCircle } from "lucide-react";

export function Header() {
  const pathname = usePathname();
  const { ready, authenticated, user, login, logout } = usePrivy();
  const [ensName, setEnsName] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  // Fallback demo address if unauthenticated
  const activeAddress = authenticated && user?.wallet?.address 
    ? user.wallet.address 
    : "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045";

  useEffect(() => {
    if (activeAddress) {
      // Fetch session and ENS from backend
      fetch("http://localhost:8000/api/v1/auth/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address: activeAddress, auth_provider: "privy" }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.ens_name) setEnsName(data.ens_name);
        })
        .catch(() => {});
    }
  }, [activeAddress]);

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await fetch(`http://localhost:8000/api/v1/portfolio/${activeAddress}/sync`, {
        method: "POST",
      });
      window.dispatchEvent(new Event("portfolio-updated"));
    } catch (e) {
      console.error("Sync failed:", e);
    } finally {
      setTimeout(() => setIsSyncing(false), 800);
    }
  };

  const navItems = [
    { href: "/", label: "Portfolio", icon: BarChart3 },
    { href: "/blotter", label: "Trade Blotter", icon: BookOpen },
    { href: "/correlation", label: "Correlation Matrix", icon: Layers },
    { href: "/reports", label: "Risk Reports", icon: FileText },
  ];

  return (
    <header style={{
      borderBottom: "1px solid var(--border-subtle)",
      background: "rgba(9, 13, 22, 0.8)",
      backdropFilter: "blur(12px)",
      position: "sticky",
      top: 0,
      zIndex: 100
    }}>
      <div style={{
        maxWidth: "1400px",
        margin: "0 auto",
        padding: "16px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "20px"
      }}>
        {/* Brand Logo */}
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none", color: "inherit" }}>
          <div style={{
            width: "36px",
            height: "36px",
            borderRadius: "10px",
            background: "var(--accent-gradient)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 0 16px rgba(99, 102, 241, 0.4)"
          }}>
            <Shield size={20} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "1.1rem", letterSpacing: "-0.01em" }}>
              Agentic Risk Manager
            </div>
            <div style={{ fontSize: "0.7rem", color: "var(--status-positive)", display: "flex", alignItems: "center", gap: "4px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--status-positive)", display: "inline-block" }}></span>
              Non-Custodial | EVM Core
            </div>
          </div>
        </Link>

        {/* Navigation Tabs */}
        <nav style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "8px 14px",
                  borderRadius: "var(--radius-sm)",
                  fontSize: "0.875rem",
                  fontWeight: 500,
                  textDecoration: "none",
                  transition: "var(--transition)",
                  background: isActive ? "rgba(99, 102, 241, 0.15)" : "transparent",
                  color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                  border: isActive ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
                }}
              >
                <Icon size={16} color={isActive ? "var(--accent-secondary)" : "currentColor"} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Actions & Wallet Session */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {/* Sync Button */}
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className="btn btn-secondary"
            style={{ padding: "8px 12px", fontSize: "0.8rem" }}
            title="Scan & sync on-chain holdings via The Graph"
          >
            <RefreshCw size={14} className={isSyncing ? "animate-spin" : ""} style={{ animation: isSyncing ? "spin 1s linear infinite" : "none" }} />
            {isSyncing ? "Syncing..." : "Sync"}
          </button>

          {/* ENS / Wallet Button */}
          {authenticated ? (
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div className="badge badge-neutral" style={{ padding: "6px 10px" }}>
                <CheckCircle size={12} color="var(--status-positive)" />
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>
                  {ensName || `${activeAddress.slice(0, 6)}...${activeAddress.slice(-4)}`}
                </span>
              </div>
              <button onClick={logout} className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "0.75rem" }}>
                Disconnect
              </button>
            </div>
          ) : (
            <button onClick={login} className="btn btn-primary" style={{ padding: "8px 16px" }}>
              <Wallet size={16} />
              Connect Wallet
            </button>
          )}
        </div>
      </div>
      <style jsx global>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </header>
  );
}
