"use client";

import React, { useState } from "react";
import { X, Send, Bot, User, Sparkles, Cpu, ArrowRight } from "lucide-react";
import { RebalanceModal } from "@/components/rebalance/RebalanceModal";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  walletAddress: string;
}

interface Message {
  sender: "user" | "copilot";
  text: string;
  toolsExecuted?: string[];
  rebalanceProposal?: any;
}

export function CopilotDrawer({ isOpen, onClose, walletAddress }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "copilot",
      text: "Hello! I am your **Agentic Risk Copilot**, powered by Uniswap AI skills. Ask me to hedge or close positions into **USDC** or **ETH**, analyze Value at Risk (VaR), or explain Greek exposures.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedRebalanceAction, setSelectedRebalanceAction] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!isOpen) return null;

  const handleSend = async (userText: string) => {
    const textToSend = userText || input;
    if (!textToSend.trim() || loading) return;

    const newMessages: Message[] = [...messages, { sender: "user", text: textToSend }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/v1/copilot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          wallet_address: walletAddress,
          message: textToSend,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages([
          ...newMessages,
          {
            sender: "copilot",
            text: data.response_text,
            toolsExecuted: data.tool_calls_executed,
            rebalanceProposal: data.proposed_rebalance,
          },
        ]);
      }
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          sender: "copilot",
          text: "I encountered an error retrieving live quantitative metrics. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "Hedge my position into USDC",
    "Convert 50% of my ETH to USDC",
    "Explain why my portfolio VaR is high",
    "Suggest a rebalance to hedge Delta",
  ];

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      backgroundColor: "rgba(0, 0, 0, 0.65)",
      backdropFilter: "blur(6px)",
      display: "flex",
      justifyContent: "flex-end",
      zIndex: 1200,
    }}>
      <div className="glass-card" style={{
        width: "100%",
        maxWidth: "460px",
        height: "100%",
        padding: "24px",
        borderRadius: "0",
        borderLeft: "1px solid var(--border-subtle)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between"
      }}>
        {/* Header */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: "var(--accent-gradient)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}>
                <Sparkles size={18} color="#fff" />
              </div>
              <div>
                <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.15rem", fontWeight: 700 }}>
                  AI Risk Copilot
                </h3>
                <div style={{ fontSize: "0.7rem", color: "var(--accent-secondary)", display: "flex", alignItems: "center", gap: "4px" }}>
                  <Cpu size={10} /> Grounded Gemini Intelligence
                </div>
              </div>
            </div>
            <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer" }}>
              <X size={20} />
            </button>
          </div>

          {/* Quick Prompts */}
          <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "16px" }}>
            {quickPrompts.map((qp, i) => (
              <button
                key={i}
                onClick={() => handleSend(qp)}
                style={{
                  textAlign: "left",
                  background: "var(--bg-glass)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "var(--radius-sm)",
                  padding: "6px 10px",
                  fontSize: "0.75rem",
                  color: "var(--text-secondary)",
                  cursor: "pointer",
                  transition: "var(--transition)"
                }}
                onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-primary)")}
                onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-secondary)")}
              >
                "{qp}"
              </button>
            ))}
          </div>
        </div>

        {/* Message Stream */}
        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "14px", paddingRight: "4px" }}>
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                gap: "10px",
                alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
                maxWidth: "90%",
              }}
            >
              {m.sender === "copilot" && (
                <div style={{ width: "28px", height: "28px", borderRadius: "50%", background: "rgba(99, 102, 241, 0.2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <Bot size={14} color="var(--accent-primary)" />
                </div>
              )}
              <div>
                <div style={{
                  background: m.sender === "user" ? "var(--accent-primary)" : "var(--bg-card-hover)",
                  color: "#fff",
                  padding: "12px 14px",
                  borderRadius: "var(--radius-md)",
                  fontSize: "0.85rem",
                  lineHeight: "1.45",
                  whiteSpace: "pre-line",
                  border: m.sender === "user" ? "none" : "1px solid var(--border-subtle)",
                }}>
                  {m.text}
                </div>

                {/* Tool Calling Badges */}
                {m.toolsExecuted && m.toolsExecuted.length > 0 && (
                  <div style={{ display: "flex", gap: "4px", flexWrap: "wrap", marginTop: "6px" }}>
                    {m.toolsExecuted.map((t, ti) => (
                      <span key={ti} className="badge badge-neutral" style={{ fontSize: "0.65rem" }}>
                        <Cpu size={8} /> {t}()
                      </span>
                    ))}
                  </div>
                )}

                {/* Interactive Uniswap AI Hedge / Rebalance Card */}
                {m.rebalanceProposal && (
                  <div style={{
                    marginTop: "10px",
                    padding: "12px",
                    background: "rgba(99, 102, 241, 0.12)",
                    border: "1px solid rgba(99, 102, 241, 0.3)",
                    borderRadius: "var(--radius-sm)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span className="badge badge-positive" style={{ fontSize: "0.7rem" }}>
                        {m.rebalanceProposal.recommended_venue === "uniswap" ? "Uniswap AI Route Ready" : "Rebalance Route"}
                      </span>
                      <span className="mono-num" style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                        {m.rebalanceProposal.source_token} $\rightarrow$ {m.rebalanceProposal.target_token}
                      </span>
                    </div>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-primary)" }}>
                      Convert <strong>{m.rebalanceProposal.amount} {m.rebalanceProposal.source_token}</strong> into <strong>{m.rebalanceProposal.target_token}</strong>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedRebalanceAction({
                          action_type: m.rebalanceProposal.action,
                          from_token: m.rebalanceProposal.source_token,
                          to_token: m.rebalanceProposal.target_token,
                          amount: m.rebalanceProposal.amount,
                          recommended_venue: m.rebalanceProposal.recommended_venue || "uniswap",
                          route_summary: m.rebalanceProposal.route_summary,
                          usd_value: m.rebalanceProposal.usd_value
                        });
                        setIsModalOpen(true);
                      }}
                      className="btn btn-primary"
                      style={{ padding: "8px 12px", fontSize: "0.8rem", gap: "6px", width: "100%", justifyContent: "center" }}
                    >
                      <ArrowRight size={14} /> Review & Sign Uniswap Hedge
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ color: "var(--text-muted)", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: "6px" }}>
              <Sparkles size={14} className="animate-spin" /> Grounding quantitative risk calculations...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(input);
          }}
          style={{ display: "flex", gap: "8px", marginTop: "16px" }}
        >
          <input
            type="text"
            placeholder="Ask Copilot about your risk..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={{ flex: 1 }}
          />
          <button type="submit" disabled={loading} className="btn btn-primary" style={{ padding: "0 14px" }}>
            <Send size={16} />
          </button>
        </form>
      </div>

      {/* Rebalance & Hedge Pre-Flight Modal */}
      {selectedRebalanceAction && (
        <RebalanceModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedRebalanceAction(null);
          }}
          action={selectedRebalanceAction}
          walletAddress={walletAddress}
        />
      )}
    </div>
  );
}
