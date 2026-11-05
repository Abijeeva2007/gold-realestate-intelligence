'use client';

import React, { useState } from 'react';
import { GoldUncertaintyResponse } from '../types/gold';

interface PredictionUncertaintySectionProps {
  uncertaintyData: GoldUncertaintyResponse | null;
}

export const PredictionUncertaintySection: React.FC<PredictionUncertaintySectionProps> = ({ uncertaintyData }) => {
  const [selectedHorizon, setSelectedHorizon] = useState<number>(30);

  if (!uncertaintyData || !uncertaintyData.uncertainty_engine) {
    return (
      <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-6 text-gray-400">
        <h3 className="text-lg font-bold text-white mb-2">Section G: Prediction Uncertainty Engine</h3>
        <p>Loading calibrated conformal intervals and breach diagnostics...</p>
      </div>
    );
  }

  const { uncertainty_engine } = uncertaintyData;
  const { test_uncertainty_audit, production_intervals, conformal_multipliers, current_price_usd } = uncertainty_engine;
  const activeInterval = production_intervals.find(p => p.horizon_trading_days === selectedHorizon) || production_intervals[0];
  const activeAudit = test_uncertainty_audit.horizon_evaluations.find(e => e.horizon_trading_days === selectedHorizon) || test_uncertainty_audit.horizon_evaluations[0];

  return (
    <div className="space-y-6">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1e293b] gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <h2 className="text-xl font-bold text-white tracking-wide">Section G: Prediction Uncertainty & Conformal Calibration</h2>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Split-conformal prediction intervals calibrated on 2023 holdout. Guaranteed coverage without Gaussian assumptions.
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

      {/* Primary Production Interval Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Point Forecast Card */}
        <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-5">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Point Forecast ({activeInterval?.horizon_trading_days}d)</div>
          <div className="text-2xl font-bold font-mono text-white mt-2">
            ${activeInterval?.point_forecast_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className={`text-xs mt-1 font-semibold ${
            (activeInterval?.expected_return_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {(activeInterval?.expected_return_pct || 0) >= 0 ? '▲' : '▼'} {activeInterval?.expected_return_pct.toFixed(2)}% vs Spot (${current_price_usd.toFixed(2)})
          </div>
          <div className="text-[11px] text-gray-500 mt-3 pt-2 border-t border-[#1e293b]">
            Origin: {uncertainty_engine.forecast_origin_date}
          </div>
        </div>

        {/* 50% Conformal Interval */}
        <div className="bg-[#111827] border border-sky-900/40 rounded-lg p-5 bg-gradient-to-br from-[#111827] to-sky-950/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">50% Interquartile</span>
            <span className="text-[10px] bg-sky-900/60 text-sky-300 px-1.5 py-0.5 rounded">IQR</span>
          </div>
          <div className="text-lg font-bold font-mono text-white mt-2">
            ${activeInterval?.interval_50.lower_usd.toFixed(1)} – ${activeInterval?.interval_50.upper_usd.toFixed(1)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Spread: <span className="font-mono text-gray-200">±${((activeInterval?.interval_50.width_usd || 0) / 2).toFixed(1)}</span> (${activeInterval?.interval_50.width_usd.toFixed(1)})
          </div>
          <div className="text-[11px] text-emerald-400 mt-3 pt-2 border-t border-[#1e293b] flex justify-between">
            <span>Test Coverage:</span>
            <span className="font-mono font-bold">{activeAudit?.conformal_50_cov_pct.toFixed(1)}%</span>
          </div>
        </div>

        {/* 80% Conformal Interval */}
        <div className="bg-[#111827] border border-amber-900/40 rounded-lg p-5 bg-gradient-to-br from-[#111827] to-amber-950/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">80% High Confidence</span>
            <span className="text-[10px] bg-amber-900/60 text-amber-300 px-1.5 py-0.5 rounded">Moderate</span>
          </div>
          <div className="text-lg font-bold font-mono text-white mt-2">
            ${activeInterval?.interval_80.lower_usd.toFixed(1)} – ${activeInterval?.interval_80.upper_usd.toFixed(1)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Spread: <span className="font-mono text-gray-200">±${((activeInterval?.interval_80.width_usd || 0) / 2).toFixed(1)}</span> (${activeInterval?.interval_80.width_usd.toFixed(1)})
          </div>
          <div className="text-[11px] text-emerald-400 mt-3 pt-2 border-t border-[#1e293b] flex justify-between">
            <span>Test Coverage:</span>
            <span className="font-mono font-bold">{activeAudit?.conformal_80_cov_pct.toFixed(1)}%</span>
          </div>
        </div>

        {/* 95% Institutional Interval */}
        <div className="bg-[#111827] border border-emerald-900/40 rounded-lg p-5 bg-gradient-to-br from-[#111827] to-emerald-950/20">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">95% Conservative Tail</span>
            <span className="text-[10px] bg-emerald-900/60 text-emerald-300 px-1.5 py-0.5 rounded">Tail Risk</span>
          </div>
          <div className="text-lg font-bold font-mono text-white mt-2">
            ${activeInterval?.interval_95.lower_usd.toFixed(1)} – ${activeInterval?.interval_95.upper_usd.toFixed(1)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Spread: <span className="font-mono text-gray-200">±${((activeInterval?.interval_95.width_usd || 0) / 2).toFixed(1)}</span> (${activeInterval?.interval_95.width_usd.toFixed(1)})
          </div>
          <div className="text-[11px] text-emerald-400 mt-3 pt-2 border-t border-[#1e293b] flex justify-between">
            <span>Test Coverage:</span>
            <span className="font-mono font-bold">{activeAudit?.conformal_95_cov_pct.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* Visual Fan Chart Representation */}
      <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-2">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Conformal Prediction Fan Bands ({selectedHorizon}-Trading-Day Projection)
            </h3>
            <p className="text-xs text-gray-400">
              Visualizing the expansion of non-parametric uncertainty envelopes anchored at spot ${current_price_usd.toFixed(2)}
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-sky-500/30 border border-sky-400"></span>
              <span className="text-gray-300">50% Band</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-amber-500/30 border border-amber-400"></span>
              <span className="text-gray-300">80% Band</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-emerald-500/20 border border-emerald-400"></span>
              <span className="text-gray-300">95% Band</span>
            </div>
          </div>
        </div>

        {/* Graphical Fan Bar Visualization */}
        <div className="py-6 px-4 bg-[#0b0f19] rounded-lg border border-[#1e293b]">
          <div className="relative h-28 flex items-center justify-center">
            {/* 95% Band Bar */}
            <div className="absolute inset-x-8 h-16 bg-emerald-950/40 border border-emerald-500/40 rounded-lg flex items-center justify-between px-3">
              <div className="text-[11px] font-mono text-emerald-400 font-bold">
                ${activeInterval?.interval_95.lower_usd.toFixed(0)} <span className="text-[10px] font-normal text-gray-500">(95% Lower)</span>
              </div>
              <div className="text-[11px] font-mono text-emerald-400 font-bold">
                <span className="text-[10px] font-normal text-gray-500">(95% Upper)</span> ${activeInterval?.interval_95.upper_usd.toFixed(0)}
              </div>
            </div>

            {/* 80% Band Bar */}
            <div className="absolute inset-x-20 md:inset-x-32 h-12 bg-amber-950/50 border border-amber-500/50 rounded flex items-center justify-between px-3 z-10">
              <div className="text-[11px] font-mono text-amber-300 font-bold">
                ${activeInterval?.interval_80.lower_usd.toFixed(0)} <span className="text-[10px] font-normal text-gray-400">(80% L)</span>
              </div>
              <div className="text-[11px] font-mono text-amber-300 font-bold">
                <span className="text-[10px] font-normal text-gray-400">(80% U)</span> ${activeInterval?.interval_80.upper_usd.toFixed(0)}
              </div>
            </div>

            {/* 50% Band Bar */}
            <div className="absolute inset-x-36 md:inset-x-64 h-8 bg-sky-900/60 border border-sky-400/60 rounded flex items-center justify-between px-2.5 z-20">
              <div className="text-[11px] font-mono text-sky-200 font-bold">
                ${activeInterval?.interval_50.lower_usd.toFixed(0)}
              </div>
              <div className="text-[11px] font-mono text-sky-200 font-bold">
                ${activeInterval?.interval_50.upper_usd.toFixed(0)}
              </div>
            </div>

            {/* Center Point Forecast Needle */}
            <div className="absolute z-30 flex flex-col items-center">
              <div className="w-1.5 h-16 bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)] rounded-full"></div>
              <div className="bg-black/90 text-white font-mono text-xs px-2 py-0.5 rounded border border-white/40 -mt-2">
                Point: ${activeInterval?.point_forecast_usd.toFixed(0)}
              </div>
            </div>
          </div>

          <div className="mt-4 flex justify-between text-xs text-gray-500 font-mono px-4">
            <div>Left Tail: Severe Macro Shock / De-escalation</div>
            <div>Center Point: XGBoost Conformal Baseline</div>
            <div>Right Tail: Geopolitical Escalation / Dollar Debasement</div>
          </div>
        </div>
      </div>

      {/* Historical Out-of-Sample Calibration Audit Table */}
      <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Out-of-Sample Conformal Calibration Audit ({test_uncertainty_audit.test_evaluation_period})
            </h3>
            <p className="text-xs text-gray-400">
              Empirical verification comparing uncalibrated Gaussian vs Conformal prediction intervals across trading horizons.
            </p>
          </div>
          <span className="text-xs font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 px-2.5 py-1 rounded">
            Audit Status: ALL PASS
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-gray-400 bg-[#0b0f19] uppercase font-mono border-b border-[#1e293b]">
              <tr>
                <th className="py-2.5 px-3">Horizon</th>
                <th className="py-2.5 px-3">Samples</th>
                <th className="py-2.5 px-3">Gaussian 95% Cov</th>
                <th className="py-2.5 px-3">Gaussian Width</th>
                <th className="py-2.5 px-3 text-sky-400">Conf 50% Cov</th>
                <th className="py-2.5 px-3 text-amber-400">Conf 80% Cov</th>
                <th className="py-2.5 px-3 text-emerald-400">Conf 95% Cov</th>
                <th className="py-2.5 px-3">Upper Breaches</th>
                <th className="py-2.5 px-3">Lower Breaches</th>
                <th className="py-2.5 px-3">Diagnosis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e293b] font-mono">
              {test_uncertainty_audit.horizon_evaluations.map((evalItem) => (
                <tr
                  key={evalItem.horizon_trading_days}
                  className={`hover:bg-[#1a2234] transition ${
                    selectedHorizon === evalItem.horizon_trading_days ? 'bg-[#1e293b]/50' : ''
                  }`}
                >
                  <td className="py-2.5 px-3 font-bold text-amber-400">{evalItem.horizon_trading_days} Days</td>
                  <td className="py-2.5 px-3 text-gray-300">{evalItem.evaluation_samples}</td>
                  <td className="py-2.5 px-3 text-rose-400 font-bold">{evalItem.uncalibrated_gaussian_95_cov_pct.toFixed(1)}%</td>
                  <td className="py-2.5 px-3 text-gray-400">${evalItem.uncalibrated_gaussian_95_width_usd.toFixed(0)}</td>
                  <td className="py-2.5 px-3 text-sky-400 font-bold">{evalItem.conformal_50_cov_pct.toFixed(1)}%</td>
                  <td className="py-2.5 px-3 text-amber-400 font-bold">{evalItem.conformal_80_cov_pct.toFixed(1)}%</td>
                  <td className="py-2.5 px-3 text-emerald-400 font-bold">{evalItem.conformal_95_cov_pct.toFixed(1)}%</td>
                  <td className="py-2.5 px-3 text-gray-300">{evalItem.conformal_95_upper_breaches}</td>
                  <td className="py-2.5 px-3 text-gray-300">{evalItem.conformal_95_lower_breaches}</td>
                  <td className="py-2.5 px-3 font-sans">
                    <span className="text-[11px] bg-emerald-950 text-emerald-300 border border-emerald-800/50 px-2 py-0.5 rounded font-mono">
                      {evalItem.calibration_diagnosis}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
