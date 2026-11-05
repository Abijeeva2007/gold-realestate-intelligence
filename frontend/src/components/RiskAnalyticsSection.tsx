"use client";

import React from "react";
import { GoldRiskResponse } from "../types/gold";

interface RiskAnalyticsSectionProps {
  riskData: GoldRiskResponse | null;
  loading: boolean;
  error?: string | null;
}

export const RiskAnalyticsSection: React.FC<RiskAnalyticsSectionProps> = ({
  riskData,
  loading,
  error,
}) => {
  if (loading) {
    return (
      <div style={{ height: "350px", background: "#111827", borderRadius: "8px", padding: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ color: "#94a3b8" }}>Loading risk analytics and stress tests...</div>
      </div>
    );
  }

  if (error || !riskData) {
    return (
      <div style={{ padding: "1rem", background: "rgba(239, 68, 68, 0.1)", border: "1px solid #ef4444", borderRadius: "8px", color: "#ef4444", marginBottom: "2rem" }}>
        ⚠️ Unable to load risk analytics: {error || "No risk records returned."}
      </div>
    );
  }

  const risk = riskData.risk_analytics;
  const vol = risk.volatility;
  const dd = risk.drawdowns;
  const varMetrics = risk.value_at_risk.metrics;

  return (
    <section id="risk" style={{ marginBottom: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", borderBottom: "1px solid #1e293b", paddingBottom: "0.5rem", marginBottom: "1rem" }}>
        <div>
          <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#f8fafc", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>🛡️</span> Section E — Quantitative Risk Analytics & Stress Testing
          </h2>
          <p style={{ fontSize: "0.75rem", color: "#64748b" }}>
            Realized volatilities, Historical Simulation VaR/CVaR, and 6 macroeconomic stress-test shock simulations.
          </p>
        </div>
      </div>

      {/* Grid of Risk Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem", marginBottom: "1rem" }}>
        <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1rem" }}>
          <div style={{ color: "#64748b", fontSize: "0.7rem", fontWeight: 600 }}>7-DAY REALIZED VOLATILITY</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#f59e0b", fontFamily: "ui-monospace", margin: "0.25rem 0" }}>
            {vol.realized_vol_7d_pct.toFixed(2)}%
          </div>
          <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>30d: {vol.realized_vol_30d_pct.toFixed(2)}% | 90d: {vol.realized_vol_90d_pct.toFixed(2)}%</div>
        </div>

        <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1rem" }}>
          <div style={{ color: "#64748b", fontSize: "0.7rem", fontWeight: 600 }}>MAX HISTORICAL DRAWDOWN</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#ef4444", fontFamily: "ui-monospace", margin: "0.25rem 0" }}>
            {dd.historical_max_drawdown_pct.toFixed(2)}%
          </div>
          <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Aug 2011 ($1,888) to Dec 2015 ($1,050)</div>
        </div>

        <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1rem" }}>
          <div style={{ color: "#64748b", fontSize: "0.7rem", fontWeight: 600 }}>VALUE AT RISK (99% 10-DAY)</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#ef4444", fontFamily: "ui-monospace", margin: "0.25rem 0" }}>
            {varMetrics.var_99pct_10d.toFixed(2)}%
          </div>
          <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Expected Shortfall (CVaR): 12.35% loss</div>
        </div>

        <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1rem" }}>
          <div style={{ color: "#64748b", fontSize: "0.7rem", fontWeight: 600 }}>ATH DRAWDOWN DURATION</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#38bdf8", fontFamily: "ui-monospace", margin: "0.25rem 0" }}>
            {dd.days_since_ath} Days
          </div>
          <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>{dd.trading_days_since_ath} Trading Days since $5,318.40</div>
        </div>
      </div>

      {/* Stress Testing Table */}
      <div style={{ background: "#111827", border: "1px solid #1e293b", borderRadius: "8px", padding: "1.25rem" }}>
        <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#f8fafc", marginBottom: "0.75rem" }}>
          MACROECONOMIC STRESS-TEST SHOCK SCENARIOS
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", textAlign: "left" }}>
            <thead>
              <tr style={{ background: "#0d131f", color: "#64748b", borderBottom: "1px solid #1e293b" }}>
                <th style={{ padding: "0.5rem" }}>SCENARIO</th>
                <th style={{ padding: "0.5rem" }}>SHOCK MAGNITUDE</th>
                <th style={{ padding: "0.5rem" }}>GOLD BETA</th>
                <th style={{ padding: "0.5rem" }}>PROJECTED RETURN</th>
                <th style={{ padding: "0.5rem" }}>PROJECTED PRICE</th>
                <th style={{ padding: "0.5rem" }}>SEVERITY</th>
              </tr>
            </thead>
            <tbody>
              {risk.stress_testing.scenarios.map((s, i) => {
                const isPositive = s.projected_return_pct >= 0;
                return (
                  <tr key={i} style={{ borderBottom: "1px solid rgba(30,41,59,0.5)", fontFamily: "ui-monospace" }}>
                    <td style={{ padding: "0.5rem", color: "#f8fafc", fontWeight: 600 }}>{s.name}</td>
                    <td style={{ padding: "0.5rem", color: "#94a3b8" }}>{s.shock_magnitude}</td>
                    <td style={{ padding: "0.5rem", color: "#f8fafc" }}>{s.gold_elasticity_beta.toFixed(2)}</td>
                    <td style={{ padding: "0.5rem", color: isPositive ? "#10b981" : "#ef4444", fontWeight: 700 }}>
                      {isPositive ? "+" : ""}{s.projected_return_pct.toFixed(2)}%
                    </td>
                    <td style={{ padding: "0.5rem", color: "#eab308", fontWeight: 600 }}>
                      ${s.projected_price_usd.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{ padding: "0.5rem", color: "#94a3b8", fontSize: "0.75rem" }}>{s.severity}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

export default RiskAnalyticsSection;
