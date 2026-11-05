"use client";

import React, { useState } from "react";
import { GoldScenariosResponse } from "../types/gold";

interface ScenarioForecastingSectionProps {
  scenarioData?: GoldScenariosResponse | null;
  scenariosData?: GoldScenariosResponse | null;
  loading?: boolean;
  error?: string | null;
}

export const ScenarioForecastingSection: React.FC<ScenarioForecastingSectionProps> = ({
  scenarioData,
  scenariosData,
  loading = false,
  error,
}) => {
  const activeData = scenarioData || scenariosData || null;
  const [activeScenario, setActiveScenario] = useState<"bullish" | "base" | "bearish">("base");

  if (loading) {
    return (
      <div style={{ height: "300px", background: "#111827", borderRadius: "8px", padding: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ color: "#94a3b8" }}>Loading conditional macro scenarios...</div>
      </div>
    );
  }

  if (error || !activeData) {
    return (
      <div style={{ padding: "1rem", background: "rgba(239, 68, 68, 0.1)", border: "1px solid #ef4444", borderRadius: "8px", color: "#ef4444", marginBottom: "2rem" }}>
        ⚠️ Unable to load scenarios: {error || "No scenario records returned."}
      </div>
    );
  }

  const scenarios = activeData.scenario_forecasts.scenarios;
  const current = scenarios[activeScenario];

  return (
    <section id="scenarios" style={{ marginBottom: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", borderBottom: "1px solid #1e293b", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
        <div>
          <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#f8fafc", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>⚡</span> Section F — Conditional Scenario Forecasting (Bullish / Base / Bearish)
          </h2>
          <p style={{ fontSize: "0.75rem", color: "#64748b" }}>
            Multi-horizon deterministic macro trajectories conditioned on specific geopolitical and real-yield policy states.
          </p>
        </div>

        {/* Scenario Switcher Tabs */}
        <div style={{ display: "flex", gap: "0.35rem", background: "#070b12", padding: "0.2rem", borderRadius: "6px", border: "1px solid #1e293b" }}>
          <button
            onClick={() => setActiveScenario("bullish")}
            style={{
              background: activeScenario === "bullish" ? "#10b981" : "transparent",
              color: activeScenario === "bullish" ? "#000" : "#94a3b8",
              border: "none",
              borderRadius: "4px",
              padding: "0.25rem 0.75rem",
              fontSize: "0.75rem",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            🟢 BULLISH ($5,850)
          </button>
          <button
            onClick={() => setActiveScenario("base")}
            style={{
              background: activeScenario === "base" ? "#eab308" : "transparent",
              color: activeScenario === "base" ? "#000" : "#94a3b8",
              border: "none",
              borderRadius: "4px",
              padding: "0.25rem 0.75rem",
              fontSize: "0.75rem",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            🟡 BASE CONSENSUS ($4,343)
          </button>
          <button
            onClick={() => setActiveScenario("bearish")}
            style={{
              background: activeScenario === "bearish" ? "#ef4444" : "transparent",
              color: activeScenario === "bearish" ? "#000" : "#94a3b8",
              border: "none",
              borderRadius: "4px",
              padding: "0.25rem 0.75rem",
              fontSize: "0.75rem",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            🔴 BEARISH ($3,200)
          </button>
        </div>
      </div>

      <div style={{
        background: "rgba(245, 158, 11, 0.08)",
        borderLeft: "3px solid #f59e0b",
        padding: "0.6rem 0.85rem",
        borderRadius: "0 4px 4px 0",
        fontSize: "0.75rem",
        color: "#94a3b8",
        marginBottom: "1rem"
      }}>
        <strong>METHODOLOGY AUDIT DISCLAIMER:</strong> {activeData.scenario_forecasts.audit_disclaimer}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1rem" }}>
        {/* Trajectory Table */}
        <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1.25rem" }}>
          <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#f8fafc", marginBottom: "0.75rem" }}>
            {current.name.toUpperCase()}
          </div>
          <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginBottom: "1rem", lineHeight: 1.4 }}>
            {current.macro_thesis}
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", textAlign: "left" }}>
              <thead>
                <tr style={{ background: "#0d131f", color: "#64748b", borderBottom: "1px solid #1e293b" }}>
                  <th style={{ padding: "0.5rem" }}>HORIZON</th>
                  <th style={{ padding: "0.5rem" }}>TARGET DATE</th>
                  <th style={{ padding: "0.5rem" }}>TARGET PRICE</th>
                  <th style={{ padding: "0.5rem" }}>RETURN (%)</th>
                  <th style={{ padding: "0.5rem" }}>RANGE BOUNDS</th>
                </tr>
              </thead>
              <tbody>
                {current.horizon_projections.map((p, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid rgba(30,41,59,0.5)", fontFamily: "ui-monospace" }}>
                    <td style={{ padding: "0.5rem", color: "#f8fafc", fontWeight: 600 }}>{p.horizon_trading_days}d</td>
                    <td style={{ padding: "0.5rem", color: "#94a3b8" }}>{p.target_calendar_date_approx}</td>
                    <td style={{ padding: "0.5rem", color: "#eab308", fontWeight: 700 }}>
                      ${p.target_price_usd.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{ padding: "0.5rem", color: p.projected_return_pct >= 0 ? "#10b981" : "#ef4444", fontWeight: 700 }}>
                      {p.projected_return_pct >= 0 ? "+" : ""}{p.projected_return_pct.toFixed(2)}%
                    </td>
                    <td style={{ padding: "0.5rem", color: "#94a3b8", fontSize: "0.75rem" }}>
                      [${p.lower_range_usd} – ${p.upper_range_usd}]
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Assumptions & Risk Factors */}
        <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1.25rem" }}>
          <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#f8fafc", marginBottom: "0.75rem" }}>
            SUPPORTING MACROECONOMIC ASSUMPTIONS
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "1rem" }}>
            {Object.entries(current.macro_assumptions).map(([k, v], idx) => (
              <div key={idx} style={{ background: "#0a0e17", padding: "0.6rem 0.75rem", borderRadius: "4px", fontSize: "0.75rem" }}>
                <span style={{ color: "#64748b", textTransform: "uppercase", fontWeight: 600 }}>{k.replace(/_/g, " ")}: </span>
                <span style={{ color: "#f8fafc" }}>{v}</span>
              </div>
            ))}
          </div>

          <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#f8fafc", marginBottom: "0.5rem" }}>
            KEY RISK FACTORS & DISCONFIRMING SIGNALS
          </div>
          <ul style={{ paddingLeft: "1.25rem", fontSize: "0.75rem", color: "#94a3b8", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
            {current.risk_factors.map((rf, idx) => (
              <li key={idx}>{rf}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
};

export default ScenarioForecastingSection;
