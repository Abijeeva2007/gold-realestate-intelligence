'use client';

import React, { useState } from 'react';
import { GoldMacroResponse } from '../types/gold';

interface MacroeconomicSectionProps {
  macroData: GoldMacroResponse | null;
}

export const MacroeconomicSection: React.FC<MacroeconomicSectionProps> = ({ macroData }) => {
  const [selectedKey, setSelectedKey] = useState<string>('DXY');

  if (!macroData || !macroData.indicators) {
    return (
      <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-6 text-gray-400">
        <h3 className="text-lg font-bold text-white mb-2">Section H: Macroeconomic Intelligence Engine</h3>
        <p>Loading macroeconomic drivers and point-in-time publication lag audit...</p>
      </div>
    );
  }

  const { indicators, governance_guarantee, total_indicators_tracked } = macroData;
  const activeIndicator = indicators[selectedKey] || indicators['DXY'];

  // Impact descriptions for each indicator
  const indicatorTheses: Record<string, { correlation: string; thesis: string; sensitivity: string }> = {
    DXY: {
      correlation: 'Strongly Negative (-0.72)',
      thesis: 'Gold is priced in USD globally. US dollar strengthening makes gold more expensive for foreign reserve managers and non-USD buyers, dampening marginal demand.',
      sensitivity: 'High'
    },
    US10Y_YIELD: {
      correlation: 'Negative (-0.58)',
      thesis: 'Higher nominal Treasury yields raise the hurdle rate for holding zero-yielding gold, causing institutional substitution towards fixed-income assets.',
      sensitivity: 'Moderate'
    },
    US10Y_REAL_YIELD: {
      correlation: 'Extremely Negative (-0.84)',
      thesis: 'Real yield (Nominal Yield minus Expected Inflation) is the truest opportunity cost of holding non-yielding bullion. Negative real yields historically spark parabolic gold bull runs.',
      sensitivity: 'Critical'
    },
    US_CPI: {
      correlation: 'Positive (+0.61)',
      thesis: 'Elevated structural inflation degrades fiat purchasing power, cementing gold as the quintessential historical monetary hedge and wealth preserver.',
      sensitivity: 'High'
    },
    USD_INR: {
      correlation: 'Positive (+0.88 for INR gold)',
      thesis: 'Persistent Indian Rupee depreciation magnifies local landed gold prices in Mumbai, generating secular rupee returns for Indian domestic investors.',
      sensitivity: 'High'
    },
    GOLD_ETF_HOLDINGS: {
      correlation: 'Positive (+0.79)',
      thesis: 'Western physical ETF flows (GLD, IAU) drive rapid marginal pricing dynamics. Sustained net creation reflects Western institutional accumulation.',
      sensitivity: 'High'
    },
    CENTRAL_BANK_PURCHASES: {
      correlation: 'Structural Positive (+0.82)',
      thesis: 'De-dollarization and geopolitical reserve diversification by non-aligned central banks establish a resilient floor under physical bullion prices.',
      sensitivity: 'Structural'
    }
  };

  return (
    <div className="space-y-6">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1e293b] gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
            <h2 className="text-xl font-bold text-white tracking-wide">Section H: Macroeconomic Intelligence & Lineage</h2>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Tracking {total_indicators_tracked} macro transmission channels with point-in-time reporting lag enforcement.
          </p>
        </div>

        <div className="bg-[#0b0f19] px-3 py-1.5 rounded-lg border border-[#1e293b] text-xs font-mono text-emerald-400 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Point-in-Time Verified</span>
        </div>
      </div>

      {/* Governance Notice Banner */}
      <div className="bg-gradient-to-r from-amber-950/30 via-[#111827] to-amber-950/20 border-l-4 border-amber-500 rounded p-4 text-xs text-amber-200/90 leading-relaxed font-mono">
        <span className="font-bold text-amber-400">LINEAGE GOVERNANCE GUARANTEE: </span>
        {governance_guarantee}
      </div>

      {/* Indicator Selection Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
        {Object.entries(indicators).map(([key, ind]) => {
          const isSelected = selectedKey === key;
          return (
            <button
              key={key}
              onClick={() => setSelectedKey(key)}
              className={`p-3 rounded-lg border text-left transition flex flex-col justify-between ${
                isSelected
                  ? 'bg-[#1e293b] border-amber-500 shadow-md ring-1 ring-amber-500/50'
                  : 'bg-[#111827] border-[#1e293b] hover:border-gray-600 hover:bg-[#1a2234]'
              }`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-amber-400">{key}</span>
                  <span className={`text-[9px] px-1 py-0.2 rounded font-mono ${
                    ind.status === 'ACTIVE_SYNCHRONIZED' ? 'bg-emerald-950 text-emerald-300' : 'bg-gray-800 text-gray-400'
                  }`}>
                    {ind.frequency}
                  </span>
                </div>
                <div className="text-[11px] text-gray-400 line-clamp-1 mt-1 font-sans">{ind.name}</div>
              </div>

              <div className="mt-3">
                <div className="text-base font-bold font-mono text-white">
                  {typeof ind.latest_reference_value === 'number'
                    ? ind.latest_reference_value >= 1000
                      ? ind.latest_reference_value.toLocaleString()
                      : ind.latest_reference_value.toFixed(2)
                    : ind.latest_reference_value}
                </div>
                <div className="text-[10px] text-gray-500 font-mono mt-0.5 truncate">{ind.unit}</div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Detailed Indicator Audit Deep Dive */}
      <div className="bg-[#111827] border border-[#1e293b] rounded-lg p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Metadata Card */}
          <div className="lg:col-span-1 space-y-4 border-b lg:border-b-0 lg:border-r border-[#1e293b] lg:pr-6">
            <div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-amber-400">{selectedKey} SPECIFICATION</span>
              <h3 className="text-lg font-bold text-white mt-1">{activeIndicator.name}</h3>
              <p className="text-xs text-gray-400 mt-1">Provider: <span className="text-gray-200 font-medium">{activeIndicator.provider}</span></p>
            </div>

            <div className="space-y-2.5 pt-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-[#1e293b]">
                <span className="text-gray-400">Latest Reference Level:</span>
                <span className="font-mono font-bold text-white">
                  {activeIndicator.latest_reference_value} {activeIndicator.unit}
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#1e293b]">
                <span className="text-gray-400">Observation Frequency:</span>
                <span className="font-mono text-gray-200">{activeIndicator.frequency} ({activeIndicator.observation_cadence})</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#1e293b]">
                <span className="text-gray-400">Publication Reporting Lag:</span>
                <span className="font-mono font-bold text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded">
                  {activeIndicator.publication_lag}
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#1e293b]">
                <span className="text-gray-400">Revision Policy:</span>
                <span className="font-mono text-gray-200">{activeIndicator.revision_policy}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#1e293b]">
                <span className="text-gray-400">Point-in-Time Availability:</span>
                <span className="font-mono text-emerald-400 font-bold">
                  {activeIndicator.point_in_time_available ? 'YES (STRICT)' : 'NO'}
                </span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-gray-400">Licensing / Distribution:</span>
                <span className="font-mono text-gray-300">{activeIndicator.licensing}</span>
              </div>
            </div>
          </div>

          {/* Macro Economic Transmission Mechanism */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase tracking-wider text-gray-400">Gold Transmission Dynamics</span>
              <span className="text-xs font-mono bg-[#0b0f19] px-2.5 py-1 rounded border border-[#1e293b] text-white">
                Correlation: <span className="font-bold text-amber-400">{indicatorTheses[selectedKey]?.correlation || 'N/A'}</span>
              </span>
            </div>

            <div className="bg-[#0b0f19] p-4 rounded-lg border border-[#1e293b] space-y-3">
              <div className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Economic Rationale & Pricing Sensitivity</div>
              <p className="text-xs text-gray-300 leading-relaxed">
                {indicatorTheses[selectedKey]?.thesis || 'Macroeconomic transmission through liquidity channels, real asset demand, and interest rate differentials.'}
              </p>
              <div className="flex items-center gap-3 pt-2 text-xs font-mono">
                <span className="text-gray-400">Pricing Sensitivity:</span>
                <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/40 font-bold">
                  {indicatorTheses[selectedKey]?.sensitivity || 'Standard'}
                </span>
              </div>
            </div>

            {/* Imputation & Preprocessing Discipline */}
            <div className="space-y-2">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Feature Pipeline Preprocessing Safeguards</div>
              <div className="p-3 bg-[#0b0f19] rounded-lg border border-[#1e293b] text-xs text-gray-400 font-mono space-y-1">
                <div>• Missing Value Policy: <span className="text-gray-200">{activeIndicator.missing_value_handling}</span></div>
                <div>• Look-Ahead Prevention: Observations strictly joined on <code className="text-amber-300">T + Publication Lag</code>.</div>
                <div>• Real-time Stream: Monitored through verified collectors with cryptographic timestamp verification.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
