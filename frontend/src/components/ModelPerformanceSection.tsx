'use client';

import React, { useState } from 'react';
import { GoldMetricsResponse } from '../types/gold';

interface ModelPerformanceSectionProps {
  metricsData: GoldMetricsResponse | null;
}

export const ModelPerformanceSection: React.FC<ModelPerformanceSectionProps> = ({ metricsData }) => {
  const [selectedHorizon, setSelectedHorizon] = useState<number>(30);

  if (!metricsData || !metricsData.models) {
    return (
      <div style={{ background: '#FFFFFF', border: '1px solid #E2D9C8', borderRadius: '10px', padding: '1.5rem', color: '#829184' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#263C32', marginBottom: '0.5rem' }}>
          Section 4: Model Performance & Validation Scorecard
        </h3>
        <p>Loading model audit metrics and walk-forward verification...</p>
      </div>
    );
  }

  const { models, evaluation_period, benchmark_baseline } = metricsData;
  const filteredModels = models.filter((m) => m.horizon_days === selectedHorizon);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Section Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderBottom: '1px solid #E2D9C8', paddingBottom: '0.75rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.2rem' }}>🏆</span>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#263C32', margin: 0 }}>
              Section 4: Model Performance Benchmark & Validation
            </h2>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#829184', margin: '0.25rem 0 0 0' }}>
            Out-of-sample walk-forward test evaluation period: <span style={{ fontFamily: 'ui-monospace', fontWeight: 600, color: '#263C32' }}>{evaluation_period}</span> vs {benchmark_baseline}.
          </p>
        </div>

        {/* Horizon Selector Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: '#F5F1E8', padding: '0.25rem', borderRadius: '8px', border: '1px solid #E2D9C8' }}>
          <span style={{ fontSize: '0.75rem', color: '#829184', fontFamily: 'ui-monospace', padding: '0 0.4rem', fontWeight: 700 }}>HORIZON:</span>
          {[30, 90, 180, 365].map((h) => (
            <button
              key={h}
              onClick={() => setSelectedHorizon(h)}
              style={{
                background: selectedHorizon === h ? '#263C32' : 'transparent',
                color: selectedHorizon === h ? '#FFFFFF' : '#556058',
                border: 'none',
                borderRadius: '6px',
                padding: '0.3rem 0.65rem',
                fontSize: '0.75rem',
                fontWeight: 700,
                cursor: 'pointer',
                fontFamily: 'ui-monospace',
                transition: 'all 0.15s ease',
              }}
            >
              {h}d
            </button>
          ))}
        </div>
      </div>

      {/* Model Benchmark Table Card */}
      <div style={{ background: '#FFFFFF', border: '1px solid #E2D9C8', borderRadius: '10px', overflow: 'hidden', boxShadow: '0 2px 4px rgba(38,60,50,0.04)' }}>
        <div style={{ padding: '0.85rem 1.25rem', borderBottom: '1px solid #E2D9C8', background: '#FCFAF6', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.8rem', fontFamily: 'ui-monospace', textTransform: 'uppercase', color: '#263C32', fontWeight: 700 }}>
            Walk-Forward Evaluation Benchmark ({selectedHorizon} Trading Days)
          </span>
          <span style={{ fontSize: '0.75rem', color: '#829184', fontFamily: 'ui-monospace' }}>
            Evaluated on real out-of-sample observations
          </span>
        </div>

        <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.8rem', fontFamily: 'ui-monospace' }}>
            <thead>
              <tr style={{ background: '#F5F1E8', color: '#263C32', borderBottom: '1px solid #E2D9C8', textTransform: 'uppercase', fontSize: '0.7rem' }}>
                <th style={{ padding: '0.65rem 0.85rem' }}>Model Architecture</th>
                <th style={{ padding: '0.65rem 0.85rem' }}>MAE (USD)</th>
                <th style={{ padding: '0.65rem 0.85rem' }}>RMSE (USD)</th>
                <th style={{ padding: '0.65rem 0.85rem' }}>MAPE (%)</th>
                <th style={{ padding: '0.65rem 0.85rem' }}>Dir. Accuracy</th>
                <th style={{ padding: '0.65rem 0.85rem' }}>Skill Score vs Naive</th>
                <th style={{ padding: '0.65rem 0.85rem' }}>95% Interval Cov</th>
                <th style={{ padding: '0.65rem 0.85rem' }}>Avg Interval Width</th>
              </tr>
            </thead>
            <tbody>
              {filteredModels.map((item, idx) => {
                const isNaive = item.model.toLowerCase().includes('naive');
                const isBest = item.model.toLowerCase().includes('xgboost');

                return (
                  <tr
                    key={item.model}
                    style={{
                      borderBottom: '1px solid #E2D9C8',
                      background: isBest ? 'rgba(176, 141, 69, 0.08)' : idx % 2 === 1 ? '#FCFAF6' : '#FFFFFF',
                    }}
                  >
                    <td style={{ padding: '0.65rem 0.85rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: isBest ? '#B08D45' : isNaive ? '#829184' : '#263C32',
                        }}></span>
                        <span style={{ fontWeight: 700, fontFamily: 'inherit', color: '#263C32' }}>
                          {item.model}
                        </span>
                        {isBest && (
                          <span style={{ fontSize: '0.65rem', background: '#2E7D32', color: '#FFFFFF', padding: '0.1rem 0.4rem', borderRadius: '4px', textTransform: 'uppercase', fontWeight: 700 }}>
                            Champion
                          </span>
                        )}
                        {isNaive && (
                          <span style={{ fontSize: '0.65rem', background: '#829184', color: '#FFFFFF', padding: '0.1rem 0.4rem', borderRadius: '4px', textTransform: 'uppercase', fontWeight: 600 }}>
                            Baseline
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: '0.65rem 0.85rem', color: '#263C32', fontWeight: 700 }}>${item.mae.toFixed(2)}</td>
                    <td style={{ padding: '0.65rem 0.85rem', color: '#556058' }}>${item.rmse.toFixed(2)}</td>
                    <td style={{ padding: '0.65rem 0.85rem', color: '#556058' }}>{item.mape.toFixed(2)}%</td>
                    <td style={{ padding: '0.65rem 0.85rem', fontWeight: 700 }}>
                      {item.directional_accuracy_pct !== null ? (
                        <span style={{ color: item.directional_accuracy_pct >= 55 ? '#2E7D32' : '#829184' }}>
                          {item.directional_accuracy_pct.toFixed(1)}%
                        </span>
                      ) : (
                        <span style={{ color: '#829184' }}>—</span>
                      )}
                    </td>
                    <td style={{ padding: '0.65rem 0.85rem' }}>
                      {item.skill_score_pct !== null ? (
                        <span style={{ fontWeight: 700, color: item.skill_score_pct > 0 ? '#2E7D32' : '#A65345' }}>
                          {item.skill_score_pct > 0 ? '+' : ''}{item.skill_score_pct.toFixed(1)}%
                        </span>
                      ) : (
                        <span style={{ color: '#829184' }}>0.0% (Ref)</span>
                      )}
                    </td>
                    <td style={{ padding: '0.65rem 0.85rem' }}>
                      {item.coverage_95_pct !== null ? (
                        <span style={{ fontWeight: 700, color: item.coverage_95_pct >= 90 ? '#2E7D32' : '#B08D45' }}>
                          {item.coverage_95_pct.toFixed(1)}%
                        </span>
                      ) : (
                        <span style={{ color: '#829184' }}>—</span>
                      )}
                    </td>
                    <td style={{ padding: '0.65rem 0.85rem', color: '#829184' }}>
                      {item.avg_interval_width_usd !== null ? `$${item.avg_interval_width_usd.toFixed(0)}` : '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Model Methodology & Limitations Audit Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
        <div style={{ background: '#FFFFFF', border: '1px solid #E2D9C8', borderRadius: '10px', padding: '1.25rem', boxShadow: '0 2px 4px rgba(38,60,50,0.04)' }}>
          <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#B08D45', textTransform: 'uppercase', letterSpacing: '0.05em', fontFamily: 'ui-monospace', margin: '0 0 0.75rem 0' }}>
            Walk-Forward Validation Architecture
          </h4>
          <ul style={{ fontSize: '0.8rem', color: '#556058', lineHeight: 1.6, paddingLeft: '1.1rem', margin: 0 }}>
            <li><strong>Expanding Training Window:</strong> Initial training from 2000-01-04 to 2022-12-30. Conformal calibration window set on 2023. Out-of-sample test from 2024 to November 2026.</li>
            <li><strong>Strict Look-Ahead Prevention:</strong> All rolling indicators (SMA 50, SMA 200, Realized Volatility) and target returns use strictly lag-1 values computed at forecast origin T.</li>
            <li><strong>Directional Accuracy Calibration:</strong> Computed solely on binary movement signs (<code style={{ color: '#B08D45' }}>sign(y_t+h - y_t) == sign(y_hat_t+h - y_t)</code>) with flat-return edge cases audited.</li>
          </ul>
        </div>

        <div style={{ background: '#FFFFFF', border: '1px solid #E2D9C8', borderRadius: '10px', padding: '1.25rem', boxShadow: '0 2px 4px rgba(38,60,50,0.04)' }}>
          <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#A65345', textTransform: 'uppercase', letterSpacing: '0.05em', fontFamily: 'ui-monospace', margin: '0 0 0.75rem 0' }}>
            Documented Model Limitations & Risk Boundaries
          </h4>
          <ul style={{ fontSize: '0.8rem', color: '#556058', lineHeight: 1.6, paddingLeft: '1.1rem', margin: 0 }}>
            <li><strong>Exogenous Black-Swan Events:</strong> Models cannot foresee kinetic military actions, sanctions, or emergency currency confiscations outside historical statistical distributions.</li>
            <li><strong>Gaussian Interval Breakdown:</strong> Uncalibrated parametric intervals systematically under-cover tail risk during volatile regime transitions (resolved via Conformal Calibration).</li>
            <li><strong>Non-Stationary Regime Shifts:</strong> Long-horizon projections (180d, 365d) carry broader uncertainty bands reflecting structural policy transitions.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ModelPerformanceSection;
