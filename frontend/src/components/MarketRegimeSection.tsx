"use client";

import React from "react";
import { GoldTrendsResponse } from "../types/gold";

interface MarketRegimeSectionProps {
  trendsData: GoldTrendsResponse | null;
  loading: boolean;
  error?: string | null;
}

export const MarketRegimeSection: React.FC<MarketRegimeSectionProps> = ({
  trendsData,
  loading,
  error,
}) => {
  if (loading) {
    return (
      <div style={{ height: "300px", background: "#111827", borderRadius: "8px", padding: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ color: "#94a3b8" }}>Loading market regime intelligence...</div>
      </div>
    );
  }

  if (error || !trendsData) {
    return (
      <div style={{ padding: "1rem", background: "rgba(239, 68, 68, 0.1)", border: "1px solid #ef4444", borderRadius: "8px", color: "#ef4444", marginBottom: "2rem" }}>
        ⚠️ Unable to load market regime intelligence: {error || "No data received."}
      </div>
    );
  }

  const analysis = trendsData.market_analysis;
  const trend = analysis.trend;
  const vol = analysis.volatility;

  return (
    <section id="regimes" style={{ marginBottom: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", borderBottom: "1px solid #1e293b", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
        <div>
          <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#f8fafc", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>🧭</span> Section D — Market Regime Intelligence
          </h2>
          <p style={{ fontSize: "0.75rem", color: "#64748b" }}>
            Multi-factor quantitative classification: Bullish, Bearish, Sideways, and High Volatility.
          </p>
        </div>
        <span style={{
          background: "rgba(245, 158, 11, 0.15)",
          border: "1px solid #f59e0b",
          color: "#f59e0b",
          padding: "0.2rem 0.6rem",
          borderRadius: "4px",
          fontSize: "0.75rem",
          fontWeight: 700,
          fontFamily: "ui-monospace"
        }}>
          ACTIVE REGIME: {analysis.current_regime.toUpperCase()}
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem" }}>
        {/* Indicators Panel */}
        <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1.25rem" }}>
          <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#f8fafc", marginBottom: "0.75rem" }}>
            TECHNICAL INDICATOR GAUGES & CONVICTION
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
            <div style={{ background: "#0a0e17", padding: "0.75rem", borderRadius: "6px" }}>
              <div style={{ fontSize: "0.65rem", color: "#64748b" }}>50-DAY MOVING AVG</div>
              <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "ui-monospace", color: "#f8fafc" }}>
                ${trend.sma_50d.toFixed(2)}
              </div>
            </div>
            <div style={{ background: "#0a0e17", padding: "0.75rem", borderRadius: "6px" }}>
              <div style={{ fontSize: "0.65rem", color: "#64748b" }}>200-DAY MOVING AVG</div>
              <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "ui-monospace", color: "#f8fafc" }}>
                ${trend.sma_200d.toFixed(2)}
              </div>
            </div>
            <div style={{ background: "#0a0e17", padding: "0.75rem", borderRadius: "6px" }}>
              <div style={{ fontSize: "0.65rem", color: "#64748b" }}>SMA CROSS RATIO (50/200)</div>
              <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "ui-monospace", color: "#ef4444" }}>
                {trend.sma_ratio.toFixed(4)} (Death Cross)
              </div>
            </div>
            <div style={{ background: "#0a0e17", padding: "0.75rem", borderRadius: "6px" }}>
              <div style={{ fontSize: "0.65rem", color: "#64748b" }}>21-DAY PRICE MOMENTUM</div>
              <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "ui-monospace", color: trend.return_21d_pct >= 0 ? "#10b981" : "#ef4444" }}>
                {trend.return_21d_pct >= 0 ? "+" : ""}{trend.return_21d_pct.toFixed(2)}%
              </div>
            </div>
          </div>
          <div style={{ marginTop: "1rem", padding: "0.75rem", background: "rgba(245, 158, 11, 0.08)", borderRadius: "6px", fontSize: "0.75rem", color: "#94a3b8" }}>
            <strong>Trend Summary:</strong> {trend.description}
          </div>
        </div>

        {/* Historical Distribution Panel */}
        <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1.25rem" }}>
          <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#f8fafc", marginBottom: "0.75rem" }}>
            26-YEAR HISTORICAL REGIME BREAKDOWN (2000–2026)
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginBottom: "0.2rem" }}>
                <span style={{ color: "#10b981", fontWeight: 600 }}>🟢 Bullish Regimes</span>
                <span style={{ fontFamily: "ui-monospace", color: "#f8fafc" }}>3,415 Days (52.0%)</span>
              </div>
              <div style={{ height: "6px", background: "#1e293b", borderRadius: "3px", overflow: "hidden" }}>
                <div style={{ width: "52%", height: "100%", background: "#10b981" }} />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginBottom: "0.2rem" }}>
                <span style={{ color: "#ef4444", fontWeight: 600 }}>🔴 Bearish Regimes</span>
                <span style={{ fontFamily: "ui-monospace", color: "#f8fafc" }}>1,764 Days (26.8%)</span>
              </div>
              <div style={{ height: "6px", background: "#1e293b", borderRadius: "3px", overflow: "hidden" }}>
                <div style={{ width: "26.8%", height: "100%", background: "#ef4444" }} />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginBottom: "0.2rem" }}>
                <span style={{ color: "#f59e0b", fontWeight: 600 }}>🟡 High Volatility Regimes</span>
                <span style={{ fontFamily: "ui-monospace", color: "#f8fafc" }}>825 Days (12.6%)</span>
              </div>
              <div style={{ height: "6px", background: "#1e293b", borderRadius: "3px", overflow: "hidden" }}>
                <div style={{ width: "12.6%", height: "100%", background: "#f59e0b" }} />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginBottom: "0.2rem" }}>
                <span style={{ color: "#38bdf8", fontWeight: 600 }}>🔵 Sideways / Consolidating</span>
                <span style={{ fontFamily: "ui-monospace", color: "#f8fafc" }}>368 Days (5.6%)</span>
              </div>
              <div style={{ height: "6px", background: "#1e293b", borderRadius: "3px", overflow: "hidden" }}>
                <div style={{ width: "5.6%", height: "100%", background: "#38bdf8" }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MarketRegimeSection;
