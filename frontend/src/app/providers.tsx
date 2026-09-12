"use client";

import React from "react";
import { PrivyProvider } from "@privy-io/react-auth";
import { WalletProvider } from "@/context/WalletContext";

export function Providers({ children }: { children: React.ReactNode }) {
  // Privy strictly requires a 25-character appId string
  const envAppId = process.env.NEXT_PUBLIC_PRIVY_APP_ID;
  const privyAppId = (envAppId && envAppId.length === 25)
    ? envAppId
    : "cmtrc963302500cla3okrcv47";

  return (
    <PrivyProvider
      appId={privyAppId}
      config={{
        loginMethods: ["wallet", "email", "sms", "google"],
        appearance: {
          theme: "dark",
          accentColor: "#6366f1", // Vibrant indigo accent
          logo: "https://cryptologos.cc/logos/ethereum-eth-logo.svg",
        },
        embeddedWallets: {
          createOnLogin: "users-without-wallets",
        },
      }}
    >
      <WalletProvider>
        {children}
      </WalletProvider>
    </PrivyProvider>
  );
}
