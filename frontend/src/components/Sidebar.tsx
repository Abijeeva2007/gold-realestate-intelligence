"use client";

import React from "react";

interface SidebarProps {
  activeSection: string;
  onSelectSection: (sectionId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeSection, onSelectSection }) => {
  const navItems = [
    { id: "market-briefing", label: "Executive Summary", icon: "🏛️", badge: "Brief" },
    { id: "overview", label: "Market Overview", icon: "📊", badge: "SEC A" },
    { id: "analysis", label: "Price Analysis", icon: "📈", badge: "SEC B" },
    { id: "forecasting", label: "Forecast Engine", icon: "🔮", badge: "SEC C" },
    { id: "regimes", label: "Market Conditions", icon: "🧭", badge: "SEC D" },
    { id: "risk", label: "Risk Analytics", icon: "🛡️", badge: "SEC E" },
    { id: "scenarios", label: "Scenario Forecasts", icon: "⚡", badge: "SEC F" },
    { id: "uncertainty", label: "Prediction Reliability", icon: "📐", badge: "SEC G" },
    { id: "macro", label: "Macro Drivers", icon: "🌐", badge: "SEC H" },
    { id: "performance", label: "Model Benchmark", icon: "🏆", badge: "SEC I" },
  ];

  return (
    <aside style={{
      width: "260px",
      backgroundColor: "#263C32",
      borderRight: "1px solid rgba(0,0,0,0.15)",
      height: "100vh",
      position: "fixed",
      top: 0,
      left: 0,
      display: "flex",
      flexDirection: "column",
      padding: "1.25rem 0.75rem",
      zIndex: 50,
      color: "#F5F1E8",
      overflowY: "auto"
    }}>
      {/* Brand Header */}
      <div style={{ padding: "0 0.5rem 1.25rem", borderBottom: "1px solid rgba(255,255,255,0.1)", marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span style={{
            background: "linear-gradient(135deg, #B08D45, #8E6F30)",
            color: "#FFFFFF",
            fontWeight: 800,
            fontSize: "0.95rem",
            width: "36px",
            height: "36px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: "6px",
            fontFamily: "Newsreader, Georgia, serif",
            border: "1px solid rgba(255,255,255,0.2)"
          }}>Au</span>
          <div>
            <div style={{ color: "#FFFFFF", fontWeight: 700, fontSize: "0.95rem", letterSpacing: "-0.01em", fontFamily: "Newsreader, Georgia, serif" }}>
              Gold Intelligence
            </div>
            <div style={{ color: "#D8C396", fontSize: "0.68rem", fontFamily: "JetBrains Mono, monospace", textTransform: "uppercase" }}>
              Global Terminal 4.1
            </div>
          </div>
        </div>

        <div style={{
          marginTop: "0.85rem",
          display: "inline-flex",
          alignItems: "center",
          gap: "0.4rem",
          background: "rgba(46, 107, 79, 0.4)",
          border: "1px solid rgba(205, 230, 214, 0.3)",
          color: "#CDE6D6",
          padding: "0.2rem 0.5rem",
          borderRadius: "4px",
          fontSize: "0.68rem",
          fontFamily: "JetBrains Mono, monospace",
          fontWeight: 600
        }}>
          <span style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#6BD499" }}></span>
          <span>SYSTEM LIVE (NOV 2026)</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.25rem" }}>
        <div style={{
          fontSize: "0.65rem",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: "#829184",
          fontWeight: 700,
          padding: "0.5rem 0.6rem 0.25rem",
          fontFamily: "JetBrains Mono, monospace"
        }}>
          Navigation
        </div>

        {navItems.map((item) => {
          const isActive = activeSection === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectSection(item.id)}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0.55rem 0.65rem",
                borderRadius: "5px",
                border: isActive ? "1px solid rgba(176, 141, 69, 0.5)" : "1px solid transparent",
                backgroundColor: isActive ? "rgba(176, 141, 69, 0.25)" : "transparent",
                color: isActive ? "#FFFFFF" : "#C8D3CC",
                fontSize: "0.825rem",
                fontWeight: isActive ? 600 : 500,
                cursor: "pointer",
                textAlign: "left",
                transition: "all 0.15s ease"
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </div>
              <span style={{
                fontSize: "0.65rem",
                fontFamily: "JetBrains Mono, monospace",
                padding: "0.1rem 0.35rem",
                borderRadius: "3px",
                backgroundColor: "rgba(0,0,0,0.25)",
                color: "#A9B8AF"
              }}>
                {item.badge}
              </span>
            </button>
          );
        })}

        {/* Real Estate Platform Switcher */}
        <div style={{ marginTop: "1rem", paddingTop: "0.75rem", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
          <a
            href="/real-estate-dashboard"
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0.55rem 0.65rem",
              backgroundColor: "rgba(176, 141, 69, 0.25)",
              border: "1px solid #B08D45",
              borderRadius: "5px",
              color: "#F5F1E8",
              textDecoration: "none",
              fontSize: "0.8rem",
              fontWeight: 600
            }}
          >
            <span>🏛️ TN Real Estate Terminal</span>
            <span style={{ fontSize: "0.65rem", color: "#D8C396" }}>↗</span>
          </a>
        </div>
      </nav>

      {/* Footer Info */}
      <div style={{
        paddingTop: "1rem",
        borderTop: "1px solid rgba(255,255,255,0.1)",
        fontSize: "0.7rem",
        color: "#9DB0A4",
        fontFamily: "JetBrains Mono, monospace"
      }}>
        <div>Store: SQLite (Unified)</div>
        <div style={{ color: "#D8C396" }}>Split-Conformal Calibrated</div>
      </div>
    </aside>
  );
};
