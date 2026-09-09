"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";

interface WalletContextType {
  activeAddress: string | null;
  ensName: string | null;
  isConnected: boolean;
  isSyncing: boolean;
  setActiveAddress: (address: string | null) => void;
  syncPortfolio: () => Promise<void>;
}

const WalletContext = createContext<WalletContextType>({
  activeAddress: null,
  ensName: null,
  isConnected: false,
  isSyncing: false,
  setActiveAddress: () => {},
  syncPortfolio: async () => {},
});

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const { authenticated, user } = usePrivy();
  const [customAddress, setCustomAddress] = useState<string | null>(null);
  const [ensName, setEnsName] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  // Read saved address on initial load if unauthenticated
  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("arm_active_address");
      if (saved && !authenticated) {
        setCustomAddress(saved);
      }
    }
  }, [authenticated]);

  // Determine active address: check primary wallet, then search linkedAccounts (embedded/social wallets)
  const linkedWallet = user?.linkedAccounts?.find(
    (account) => account.type === "wallet" && "address" in account
  ) as { address?: string } | undefined;

  const privyAddress = user?.wallet?.address || linkedWallet?.address || null;

  const activeAddress = authenticated && privyAddress
    ? privyAddress
    : customAddress;

  // Resolve ENS and sync session when activeAddress changes
  useEffect(() => {
    if (activeAddress) {
      fetch("http://localhost:8000/api/v1/auth/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address: activeAddress, auth_provider: authenticated ? "privy" : "explorer" }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.ens_name) {
            setEnsName(data.ens_name);
          } else {
            setEnsName(null);
          }
        })
        .catch(() => setEnsName(null));
    } else {
      setEnsName(null);
    }
  }, [activeAddress, authenticated]);

  const handleSetActiveAddress = (address: string | null) => {
    setCustomAddress(address);
    if (typeof window !== "undefined") {
      if (address) {
        localStorage.setItem("arm_active_address", address);
      } else {
        localStorage.removeItem("arm_active_address");
      }
    }
    window.dispatchEvent(new Event("portfolio-updated"));
  };

  const syncPortfolio = async () => {
    if (!activeAddress) return;
    setIsSyncing(true);
    try {
      await fetch(`http://localhost:8000/api/v1/portfolio/${activeAddress}/sync`, {
        method: "POST",
      });
      window.dispatchEvent(new Event("portfolio-updated"));
    } catch (e) {
      console.error("Failed to sync on-chain balances:", e);
    } finally {
      setTimeout(() => setIsSyncing(false), 800);
    }
  };

  return (
    <WalletContext.Provider
      value={{
        activeAddress,
        ensName,
        isConnected: Boolean(authenticated && privyAddress),
        isSyncing,
        setActiveAddress: handleSetActiveAddress,
        syncPortfolio,
      }}
    >
      {children}
    </WalletContext.Provider>
  );
}

export const useActiveWallet = () => useContext(WalletContext);
