"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { usePrivy } from "@privy-io/react-auth";
import { useActiveWallet } from "@/context/WalletContext";
import { Shield, Wallet, RefreshCw, BarChart3, BookOpen, Layers, FileText, CheckCircle, Search, X } from "lucide-react";

export function Header() {
  const pathname = usePathname();
  const { authenticated, login, logout } = usePrivy();
  const { activeAddress, ensName, isConnected, isSyncing, setActiveAddress, syncPortfolio } = useActiveWallet();

  const [inputAddress, setInputAddress] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  const handleInspectSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = inputAddress.trim();
    if (!clean) return;
    setActiveAddress(clean);
    setIsSearching(false);
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
              Live Multi-Chain | Real Holdings Only
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

        {/* Address Search & Wallet Session Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Quick Inspect Input Toggle */}
          {isSearching ? (
            <form onSubmit={handleInspectSubmit} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <input
                type="text"
                placeholder="Enter 0x... address"
                value={inputAddress}
                onChange={(e) => setInputAddress(e.target.value)}
                style={{
                  padding: "6px 10px",
                  background: "var(--bg-elevated)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)",
                  fontSize: "0.8rem",
                  width: "200px"
                }}
                autoFocus
              />
              <button type="submit" className="btn btn-primary" style={{ padding: "6px 10px", fontSize: "0.75rem" }}>
                Load
              </button>
              <button type="button" onClick={() => setIsSearching(false)} className="btn btn-secondary" style={{ padding: "6px 8px" }}>
                <X size={12} />
              </button>
            </form>
          ) : (
            <button
              onClick={() => setIsSearching(true)}
              className="btn btn-secondary"
              style={{ padding: "8px 10px", fontSize: "0.8rem" }}
              title="Inspect any public address"
            >
              <Search size={14} />
              <span>Inspect</span>
            </button>
          )}

          {/* Sync On-Chain Button */}
          {activeAddress && (
            <button
              onClick={syncPortfolio}
              disabled={isSyncing}
              className="btn btn-secondary"
              style={{ padding: "8px 12px", fontSize: "0.8rem" }}
              title="Rescan on-chain balances across 5 EVM chains"
            >
              <RefreshCw size={14} style={{ animation: isSyncing ? "spin 1s linear infinite" : "none" }} />
              {isSyncing ? "Scanning..." : "Sync"}
            </button>
          )}

          {/* Active Wallet Display / Privy Login */}
          {isConnected && activeAddress ? (
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
          ) : activeAddress ? (
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <div className="badge badge-neutral" style={{ padding: "6px 10px" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--accent-secondary)", marginRight: "4px" }}>Viewing:</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>
                  {ensName || `${activeAddress.slice(0, 6)}...${activeAddress.slice(-4)}`}
                </span>
              </div>
              <button
                onClick={() => setActiveAddress(null)}
                className="btn btn-secondary"
                style={{ padding: "6px 8px" }}
                title="Clear address"
              >
                <X size={12} />
              </button>
              <button onClick={login} className="btn btn-primary" style={{ padding: "8px 14px", fontSize: "0.8rem" }}>
                <Wallet size={14} />
                Connect
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
