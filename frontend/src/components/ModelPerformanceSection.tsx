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
      <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-6 text-gray-400">
        <h3 className="text-lg font-bold text-white mb-2">Section I: Model Performance & Validation Scorecard</h3>
        <p>Loading model audit metrics and walk-forward verification...</p>
      </div>
    );
  }

  const { models, evaluation_period, benchmark_baseline } = metricsData;
  const filteredModels = models.filter(m => m.horizon_days === selectedHorizon);

  return (
    <div className="space-y-6">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1e293b] gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400"></span>
            <h2 className="text-xl font-bold text-white tracking-wide">Section I: Model Performance Benchmark & Validation</h2>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Out-of-sample walk-forward test evaluation period: <span className="font-mono text-gray-200">{evaluation_period}</span> vs {benchmark_baseline}.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-[#0b0f19] p-1.5 rounded-lg border border-[#1e293b]">
          <span className="text-xs text-gray-400 font-mono pl-2">Trading Horizon:</span>
          {[30, 90, 180, 365].map((h) => (
            <button
              key={h}
              onClick={() => setSelectedHorizon(h)}
              className={`px-3 py-1 text-xs font-semibold rounded transition ${
                selectedHorizon === h
                  ? 'bg-amber-500 text-black shadow'
                  : 'text-gray-400 hover:text-white hover:bg-[#1f293d]'
              }`}
            >
              {h}d
            </button>
          ))}
        </div>
      </div>

      {/* Model Benchmark Table */}
      <div className="bg-[#111827] border border-[#1e293b] rounded-lg overflow-hidden shadow">
        <div className="p-4 border-b border-[#1e293b] bg-[#0b0f19]/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <span className="text-xs font-mono uppercase tracking-wider text-gray-300 font-bold">
            Walk-Forward Evaluation Benchmark ({selectedHorizon} Trading Days)
          </span>
          <span className="text-xs text-gray-400 font-mono">
            Evaluated on real out-of-sample observations
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#0b0f19] text-gray-400 uppercase text-[11px] border-b border-[#1e293b]">
              <tr>
                <th className="py-3 px-4">Model Architecture</th>
                <th className="py-3 px-4">MAE (USD)</th>
                <th className="py-3 px-4">RMSE (USD)</th>
                <th className="py-3 px-4">MAPE (%)</th>
                <th className="py-3 px-4">Dir. Accuracy</th>
                <th className="py-3 px-4">Skill Score vs Naive</th>
                <th className="py-3 px-4">95% Interval Cov</th>
                <th className="py-3 px-4">Avg Interval Width</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e293b]">
              {filteredModels.map((item) => {
                const isNaive = item.model.toLowerCase().includes('naive');
                const isBest = item.model.toLowerCase().includes('xgboost');

                return (
                  <tr
                    key={item.model}
                    className={`hover:bg-[#1a2234] transition ${
                      isBest ? 'bg-amber-950/20' : ''
                    }`}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${
                          isBest ? 'bg-amber-400' : isNaive ? 'bg-gray-400' : 'bg-sky-400'
                        }`}></span>
                        <span className={`font-bold font-sans ${isBest ? 'text-amber-300' : 'text-white'}`}>
                          {item.model}
                        </span>
                        {isBest && (
                          <span className="text-[9px] bg-amber-500/20 text-amber-300 border border-amber-500/40 px-1.5 py-0.2 rounded uppercase">
                            Champion
                          </span>
                        )}
                        {isNaive && (
                          <span className="text-[9px] bg-gray-700 text-gray-300 px-1.5 py-0.2 rounded uppercase">
                            Baseline
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-200 font-bold">${item.mae.toFixed(2)}</td>
                    <td className="py-3 px-4 text-gray-200">${item.rmse.toFixed(2)}</td>
                    <td className="py-3 px-4 text-gray-200">{item.mape.toFixed(2)}%</td>
                    <td className="py-3 px-4 font-bold">
                      {item.directional_accuracy_pct !== null ? (
                        <span className={item.directional_accuracy_pct >= 55 ? 'text-emerald-400' : 'text-gray-400'}>
                          {item.directional_accuracy_pct.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-gray-500">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {item.skill_score_pct !== null ? (
                        <span className={`font-bold ${item.skill_score_pct > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {item.skill_score_pct > 0 ? '+' : ''}{item.skill_score_pct.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-gray-500">0.0% (Ref)</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {item.coverage_95_pct !== null ? (
                        <span className={`font-bold ${item.coverage_95_pct >= 90 ? 'text-emerald-400' : 'text-amber-400'}`}>
                          {item.coverage_95_pct.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-gray-500">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-400">
                      {item.avg_interval_width_usd !== null ? `$${item.avg_interval_width_usd.toFixed(0)}` : '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Model Methodology & Limitations Audit */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-5 space-y-3">
          <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono">
            Walk-Forward Validation Architecture
          </h4>
          <ul className="text-xs text-gray-300 space-y-2 leading-relaxed">
            <li className="flex items-start gap-2">
              <span className="text-amber-400 font-bold">•</span>
              <span><strong>Expanding Training Window:</strong> Initial training from 2000-01-04 to 2022-12-30. Conformal calibration window set on 2023. Out-of-sample test from 2024 to November 2026.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-400 font-bold">•</span>
              <span><strong>Strict Look-Ahead Prevention:</strong> All rolling indicators (SMA 50, SMA 200, Realized Volatility) and target returns use strictly lag-1 values computed at forecast origin T.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-400 font-bold">•</span>
              <span><strong>Directional Accuracy Calibration:</strong> Computed solely on binary movement signs (<code className="text-amber-300">sign(y_t+h - y_t) == sign(y_hat_t+h - y_t)</code>) with flat-return edge cases audited.</span>
            </li>
          </ul>
        </div>

        <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-5 space-y-3">
          <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider font-mono">
            Documented Model Limitations & Risk Boundaries
          </h4>
          <ul className="text-xs text-gray-300 space-y-2 leading-relaxed">
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold">•</span>
              <span><strong>Exogenous Black-Swan Events:</strong> Models cannot foresee kinetic military actions, sanctions, or emergency currency confiscations outside historical statistical distributions.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold">•</span>
              <span><strong>Gaussian Interval Breakdown:</strong> Uncalibrated parametric intervals systematically under-cover tail risk during volatile regime transitions (resolved via Conformal Calibration).</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold">•</span>
              <span><strong>Non-Stationary Regime Shifts:</strong> Long-horizon projections (180d, 365d) carry broader uncertainty bands reflecting structural policy transitions.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
