"use client";

import React, { useState } from "react";
import { GoldForecastResponse, GoldMetricsResponse } from "../types/gold";

interface ForecastingSectionProps {
  forecastData: GoldForecastResponse | null;
  metricsData: GoldMetricsResponse | null;
  loading: boolean;
  error?: string | null;
}

interface HorizonGuidance {
  days: number;
  label: string;
  targetDate: string;
  usdSpot: number;
  usdChange: number;
  usdChangePct: number;
  baseSovRate: number;
  baseSovChange: number;
  showroomSovRate: number;
  trend: string;
  recommendation: string;
  actionClass: "bull" | "side";
}

export const ForecastingSection: React.FC<ForecastingSectionProps> = ({
  forecastData,
  metricsData,
  loading,
  error,
}) => {
  const [selectedHorizon, setSelectedHorizon] = useState<number>(90);

  const HORIZON_GUIDANCE: HorizonGuidance[] = [
    {
      days: 30,
      label: "30 Trading Days",
      targetDate: "2026-12-16",
      usdSpot: 4076.68,
      usdChange: 3.68,
      usdChangePct: 0.09,
      baseSovRate: 107176,
      baseSovChange: 96,
      showroomSovRate: 121431,
      trend: "Flat / Stable",
      recommendation: "Minimal price change. Safe window for routine monthly gold accumulation.",
      actionClass: "side",
    },
    {
      days: 90,
      label: "90 Trading Days",
      targetDate: "2027-03-14",
      usdSpot: 4259.34,
      usdChange: 186.34,
      usdChangePct: 4.58,
      baseSovRate: 111984,
      baseSovChange: 4904,
      showroomSovRate: 126878,
      trend: "Rising ▲",
      recommendation: "Buy in advance! If purchasing jewellery for 3-month wedding season, buying now saves ~₹4,900 per sovereign.",
      actionClass: "bull",
    },
    {
      days: 180,
      label: "180 Trading Days",
      targetDate: "2027-07-23",
      usdSpot: 4145.23,
      usdChange: 72.23,
      usdChangePct: 1.77,
      baseSovRate: 108975,
      baseSovChange: 1895,
      showroomSovRate: 123468,
      trend: "Consolidation",
      recommendation: "Temporary mid-year consolidation offers attractive accumulation entry points.",
      actionClass: "side",
    },
    {
      days: 365,
      label: "365 Trading Days",
      targetDate: "2028-04-16",
      usdSpot: 4343.01,
      usdChange: 270.01,
      usdChangePct: 6.63,
      baseSovRate: 114179,
      baseSovChange: 7099,
      showroomSovRate: 129365,
      trend: "Strong Rise ▲",
      recommendation: "Long-term structural rise. 1 Sovereign projected to exceed ₹1.14L base (₹1.29L showroom).",
      actionClass: "bull",
    },
  ];

  if (loading) {
    return (
      <div style={{ height: "350px", background: "#FFFFFF", border: "1px solid #E2D9C8", borderRadius: "10px", padding: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ color: "#829184" }}>Loading multi-horizon forecasts & 1-Sovereign retail projections...</div>
      </div>
    );
  }

  if (error || !forecastData) {
    return (
      <div style={{ padding: "1rem", background: "rgba(166, 83, 69, 0.08)", border: "1px solid #A65345", borderRadius: "8px", color: "#A65345", marginBottom: "2rem" }}>
        ⚠️ Unable to load forecasts: {error || "No forecast records available."}
      </div>
    );
  }

  const forecastsForHorizon = forecastData.forecasts.filter((f) => f.horizon_days === selectedHorizon);
  const metricsForHorizon = (metricsData?.models || []).filter((m) => m.horizon_days === selectedHorizon);
  const activeGuidance = HORIZON_GUIDANCE.find((g) => g.days === selectedHorizon) || HORIZON_GUIDANCE[1];

  return (
    <section id="forecasting" style={{ marginBottom: "2.5rem" }}>
      {/* Section Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", borderBottom: "1px solid #E2D9C8", paddingBottom: "0.75rem", marginBottom: "1.25rem" }}>
        <div>
          <h2 style={{ fontSize: "1.3rem", fontWeight: 700, color: "#263C32", display: "flex", alignItems: "center", gap: "0.5rem", margin: 0 }}>
            <span>🔮</span> Section 3: Price Prediction & Common-Man Jewellery Trends
          </h2>
          <p style={{ fontSize: "0.85rem", color: "#829184", margin: "0.25rem 0 0 0" }}>
            Forecasts for 1 Sovereign (8g 22K) gold in Tamil Nadu & model predictions anchored on November 4, 2026 ($4,073.00/oz).
          </p>
        </div>

        {/* Horizon Switcher Tabs */}
        <div style={{ display: "flex", gap: "0.35rem", background: "#F5F1E8", padding: "0.25rem", borderRadius: "8px", border: "1px solid #E2D9C8" }}>
          {HORIZON_GUIDANCE.map((h) => (
            <button
              key={h.days}
              onClick={() => setSelectedHorizon(h.days)}
              style={{
                background: selectedHorizon === h.days ? "#263C32" : "transparent",
                color: selectedHorizon === h.days ? "#FFFFFF" : "#556058",
                border: "none",
                borderRadius: "6px",
                padding: "0.35rem 0.75rem",
                fontSize: "0.75rem",
                fontWeight: 700,
                cursor: "pointer",
                fontFamily: "ui-monospace",
                transition: "all 0.15s ease",
              }}
            >
              {h.days}D ({h.days === 90 ? "3 Mo" : h.days === 180 ? "6 Mo" : h.days === 365 ? "1 Yr" : "1 Mo"})
            </button>
          ))}
        </div>
      </div>

      {/* 1 Sovereign Common-Man Forecast Banner */}
      <div style={{
        background: "#FCFAF6",
        border: "1.5px solid #B08D45",
        borderRadius: "10px",
        padding: "1.25rem",
        marginBottom: "1.5rem",
        boxShadow: "0 2px 6px rgba(38,60,50,0.04)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem", borderBottom: "1px solid #E2D9C8", paddingBottom: "0.75rem", marginBottom: "1rem" }}>
          <div>
            <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "#829184", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              CURRENT TAMIL NADU BENCHMARK (NOV 5, 2026)
            </span>
            <div style={{ display: "flex", alignItems: "baseline", gap: "0.75rem", marginTop: "0.25rem" }}>
              <span style={{ fontSize: "1.75rem", fontWeight: 800, color: "#263C32", fontFamily: "ui-monospace" }}>
                ₹1,07,080
              </span>
              <span style={{ fontSize: "0.9rem", color: "#B08D45", fontWeight: 700 }}>
                1 Sovereign (8g 22K) @ ₹13,385 / gram
              </span>
            </div>
          </div>

          <div style={{
            background: activeGuidance.actionClass === "bull" ? "rgba(46, 125, 50, 0.12)" : "rgba(176, 141, 69, 0.12)",
            border: `1px solid ${activeGuidance.actionClass === "bull" ? "#2E7D32" : "#B08D45"}`,
            borderRadius: "6px",
            padding: "0.4rem 0.8rem",
            textAlign: "right"
          }}>
            <div style={{ fontSize: "0.7rem", color: "#556058", textTransform: "uppercase", fontWeight: 700 }}>
              {activeGuidance.days}-Day Outlook:
            </div>
            <div style={{ fontSize: "0.95rem", fontWeight: 800, color: activeGuidance.actionClass === "bull" ? "#2E7D32" : "#8C6A28" }}>
              {activeGuidance.trend} ({activeGuidance.baseSovChange >= 0 ? "+" : ""}₹{activeGuidance.baseSovChange.toLocaleString("en-IN")})
            </div>
          </div>
        </div>

        {/* 4 Horizons Summary Table */}
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem", textAlign: "left" }}>
            <thead>
              <tr style={{ background: "#F5F1E8", color: "#263C32", borderBottom: "1.5px solid #E2D9C8" }}>
                <th style={{ padding: "0.6rem 0.75rem" }}>TRADING HORIZON</th>
                <th style={{ padding: "0.6rem 0.75rem" }}>TARGET DATE</th>
                <th style={{ padding: "0.6rem 0.75rem" }}>COMEX SPOT ($)</th>
                <th style={{ padding: "0.6rem 0.75rem" }}>1 SOV BASE (8g 22K)</th>
                <th style={{ padding: "0.6rem 0.75rem" }}>SHOWROOM EST*</th>
                <th style={{ padding: "0.6rem 0.75rem" }}>COMMON-MAN BUYING ADVICE</th>
              </tr>
            </thead>
            <tbody>
              {HORIZON_GUIDANCE.map((g) => {
                const isSelected = g.days === selectedHorizon;
                return (
                  <tr
                    key={g.days}
                    onClick={() => setSelectedHorizon(g.days)}
                    style={{
                      borderBottom: "1px solid #E2D9C8",
                      background: isSelected ? "rgba(176, 141, 69, 0.09)" : "transparent",
                      cursor: "pointer",
                      fontFamily: "ui-monospace"
                    }}
                  >
                    <td style={{ padding: "0.65rem 0.75rem", fontWeight: isSelected ? 800 : 600, color: "#263C32" }}>
                      {g.label} {isSelected && "👈"}
                    </td>
                    <td style={{ padding: "0.65rem 0.75rem", color: "#556058" }}>{g.targetDate}</td>
                    <td style={{ padding: "0.65rem 0.75rem", color: "#B08D45", fontWeight: 700 }}>
                      ${g.usdSpot.toFixed(2)} ({g.usdChangePct >= 0 ? "+" : ""}{g.usdChangePct.toFixed(2)}%)
                    </td>
                    <td style={{ padding: "0.65rem 0.75rem", color: "#263C32", fontWeight: 800 }}>
                      ₹{g.baseSovRate.toLocaleString("en-IN")}{" "}
                      <span style={{ fontSize: "0.75rem", color: g.baseSovChange >= 0 ? "#2E7D32" : "#A65345", fontWeight: 700 }}>
                        ({g.baseSovChange >= 0 ? "+" : ""}₹{g.baseSovChange.toLocaleString("en-IN")})
                      </span>
                    </td>
                    <td style={{ padding: "0.65rem 0.75rem", color: "#8C6A28", fontWeight: 700 }}>
                      ₹{g.showroomSovRate.toLocaleString("en-IN")}
                    </td>
                    <td style={{ padding: "0.65rem 0.75rem", fontFamily: "sans-serif", fontSize: "0.8rem", color: "#343A36" }}>
                      {g.recommendation}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div style={{ marginTop: "0.6rem", fontSize: "0.75rem", color: "#829184" }}>
          *Showroom Estimate includes typical Tamil Nadu jeweller making charges (10% VA/wastage) + statutory 3% GST.
        </div>
      </div>

      {/* Grid: Model Predictions & Out-of-Sample Accuracy */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1rem" }}>
        {/* Model Predictions Table */}
        <div style={{ background: "#FFFFFF", border: "1px solid #E2D9C8", borderRadius: "10px", padding: "1.25rem", boxShadow: "0 2px 4px rgba(38,60,50,0.04)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.75rem", alignItems: "center" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#263C32" }}>
              INDIVIDUAL MODELS ({selectedHorizon}-DAY HORIZON)
            </span>
            <span style={{ fontSize: "0.7rem", color: "#829184", fontFamily: "ui-monospace" }}>
              Target: {forecastsForHorizon[0]?.target_date_approx || activeGuidance.targetDate}
            </span>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", textAlign: "left" }}>
              <thead>
                <tr style={{ background: "#F5F1E8", color: "#556058", borderBottom: "1px solid #E2D9C8" }}>
                  <th style={{ padding: "0.5rem" }}>MODEL</th>
                  <th style={{ padding: "0.5rem" }}>POINT TARGET ($)</th>
                  <th style={{ padding: "0.5rem" }}>95% INTERVAL</th>
                  <th style={{ padding: "0.5rem" }}>RETURN</th>
                </tr>
              </thead>
              <tbody>
                {forecastsForHorizon.map((f, i) => {
                  const isPositive = f.forecast_return_pct >= 0;
                  return (
                    <tr key={i} style={{ borderBottom: "1px solid #E2D9C8", fontFamily: "ui-monospace" }}>
                      <td style={{ padding: "0.5rem", color: "#263C32", fontWeight: 600 }}>{f.model}</td>
                      <td style={{ padding: "0.5rem", color: "#B08D45", fontWeight: 700 }}>
                        ${f.point_forecast_usd.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                      </td>
                      <td style={{ padding: "0.5rem", color: "#556058", fontSize: "0.75rem" }}>
                        [${f.lower_bound_95_usd.toFixed(2)} – ${f.upper_bound_95_usd.toFixed(2)}]
                      </td>
                      <td style={{ padding: "0.5rem", color: isPositive ? "#2E7D32" : "#A65345", fontWeight: 700 }}>
                        {isPositive ? "+" : ""}{f.forecast_return_pct.toFixed(2)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Validation Accuracy Metrics Table */}
        <div style={{ background: "#FFFFFF", border: "1px solid #E2D9C8", borderRadius: "10px", padding: "1.25rem", boxShadow: "0 2px 4px rgba(38,60,50,0.04)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.75rem", alignItems: "center" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#263C32" }}>
              OUT-OF-SAMPLE TEST ACCURACY ({selectedHorizon}D)
            </span>
            <span style={{ fontSize: "0.7rem", color: "#829184", fontFamily: "ui-monospace" }}>
              2024–2026 Test Period
            </span>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", textAlign: "left" }}>
              <thead>
                <tr style={{ background: "#F5F1E8", color: "#556058", borderBottom: "1px solid #E2D9C8" }}>
                  <th style={{ padding: "0.5rem" }}>MODEL</th>
                  <th style={{ padding: "0.5rem" }}>MAE ($)</th>
                  <th style={{ padding: "0.5rem" }}>MAPE (%)</th>
                  <th style={{ padding: "0.5rem" }}>DIR ACC (%)</th>
                  <th style={{ padding: "0.5rem" }}>SKILL</th>
                </tr>
              </thead>
              <tbody>
                {metricsForHorizon.map((m, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #E2D9C8", fontFamily: "ui-monospace" }}>
                    <td style={{ padding: "0.5rem", color: "#263C32", fontWeight: 600 }}>{m.model}</td>
                    <td style={{ padding: "0.5rem", color: "#556058" }}>${m.mae.toFixed(2)}</td>
                    <td style={{ padding: "0.5rem", color: "#556058" }}>{m.mape.toFixed(2)}%</td>
                    <td style={{ padding: "0.5rem", color: m.directional_accuracy_pct && m.directional_accuracy_pct > 60 ? "#2E7D32" : "#556058", fontWeight: 700 }}>
                      {m.directional_accuracy_pct ? `${m.directional_accuracy_pct.toFixed(2)}%` : "N/A"}
                    </td>
                    <td style={{ padding: "0.5rem", color: m.skill_score_pct && m.skill_score_pct > 0 ? "#2E7D32" : "#556058" }}>
                      {m.skill_score_pct ? `${m.skill_score_pct > 0 ? "+" : ""}${m.skill_score_pct.toFixed(2)}%` : "Baseline"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: "0.75rem", fontSize: "0.7rem", color: "#829184" }}>
            *Directional accuracy evaluates concordance of projected price direction vs actual historical movement.
          </div>
        </div>
      </div>
    </section>
  );
};

export default ForecastingSection;
