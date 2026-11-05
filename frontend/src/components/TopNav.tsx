"use client";

import React from "react";

interface TopNavProps {
  lastUpdated: string;
  isRefreshing: boolean;
  onRefresh: () => void;
  spotPrice?: number;
  ath?: number;
  currentDrawdown?: number;
  regime?: string;
}

export const TopNav: React.FC<TopNavProps> = ({
  lastUpdated,
  isRefreshing,
  onRefresh,
  spotPrice = 4073.0,
  ath = 5318.4,
  currentDrawdown = -23.42,
  regime = "High Volatility",
}) => {
  return (
    <header style={{
      height: "56px",
      backgroundColor: "#05080f",
      borderBottom: "1px solid #1e293b",
      padding: "0 1.5rem",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      position: "sticky",
      top: 0,
      zIndex: 30,
    }}>
      {/* Ticker Stream */}
      <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", fontSize: "0.8rem", fontFamily: "ui-monospace" }}>
        <div style={{ display: "flex", gap: "0.35rem" }}>
          <span style={{ color: "#64748b" }}>COMEX GOLD:</span>
          <span style={{ color: "#eab308", fontWeight: 700 }}>${spotPrice.toLocaleString("en-US", { minimumFractionDigits: 2 })}</span>
        </div>
        <div style={{ display: "flex", gap: "0.35rem" }}>
          <span style={{ color: "#64748b" }}>ATH:</span>
          <span style={{ color: "#f8fafc", fontWeight: 600 }}>${ath.toLocaleString("en-US", { minimumFractionDigits: 2 })}</span>
        </div>
        <div style={{ display: "flex", gap: "0.35rem" }}>
          <span style={{ color: "#64748b" }}>ATH DD:</span>
          <span style={{ color: currentDrawdown < 0 ? "#ef4444" : "#10b981", fontWeight: 700 }}>
            {currentDrawdown.toFixed(2)}%
          </span>
        </div>
        <div style={{ display: "flex", gap: "0.35rem" }}>
          <span style={{ color: "#64748b" }}>REGIME:</span>
          <span style={{ color: "#f59e0b", fontWeight: 700, textTransform: "uppercase" }}>
            {regime}
          </span>
        </div>
      </div>

      {/* Controls & Timestamp */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <div style={{ textAlign: "right", fontSize: "0.7rem", fontFamily: "ui-monospace" }}>
          <div style={{ color: "#64748b" }}>LAST AUDIT / REFRESH</div>
          <div style={{ color: "#94a3b8", fontWeight: 600 }}>{lastUpdated || "2026-11-04 17:00 EST"}</div>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          style={{
            background: isRefreshing ? "#1e293b" : "rgba(234, 179, 8, 0.15)",
            border: "1px solid #eab308",
            color: "#eab308",
            fontSize: "0.75rem",
            fontWeight: 700,
            padding: "0.4rem 0.8rem",
            borderRadius: "4px",
            cursor: isRefreshing ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            gap: "0.4rem",
            transition: "all 0.15s ease",
            fontFamily: "ui-monospace"
          }}
        >
          <span>{isRefreshing ? "⏳" : "↻"}</span>
          <span>{isRefreshing ? "REFRESHING..." : "SYNC FEED"}</span>
        </button>
      </div>
    </header>
  );
};

export default TopNav;
