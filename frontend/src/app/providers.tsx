"use client";

import React from "react";
import { PrivyProvider } from "@privy-io/react-auth";

export function Providers({ children }: { children: React.ReactNode }) {
  // Use mock or user-provided Privy App ID
  const privyAppId = process.env.NEXT_PUBLIC_PRIVY_APP_ID || "clrw6z0mockprivyappid";

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
      {children}
    </PrivyProvider>
  );
}
