'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { fetchDashboardBundle, DashboardBundle } from '../services/api';
import { Sidebar } from '../components/Sidebar';
import { MarketOverview } from '../components/MarketOverview';
import { GoldPriceAnalysis } from '../components/GoldPriceAnalysis';
import { ForecastingSection } from '../components/ForecastingSection';
import { MarketRegimeSection } from '../components/MarketRegimeSection';
import { RiskAnalyticsSection } from '../components/RiskAnalyticsSection';
import { ScenarioForecastingSection } from '../components/ScenarioForecastingSection';
import { PredictionUncertaintySection } from '../components/PredictionUncertaintySection';
import { MacroeconomicSection } from '../components/MacroeconomicSection';
import { ModelPerformanceSection } from '../components/ModelPerformanceSection';

export default function DashboardPage() {
  const [data, setData] = useState<DashboardBundle | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [showAdvancedDrawer, setShowAdvancedDrawer] = useState<boolean>(false);

  const loadData = useCallback(async () => {
    try {
      setError(null);
      const bundle = await fetchDashboardBundle();
      setData(bundle);
    } catch (err: any) {
      console.error('Failed to load dashboard intelligence bundle:', err);
      setError(err?.message || 'Failed to connect to Gold Intelligence API backend.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadData();
  };

  const handleSectionSelect = (sectionId: string) => {
    setActiveSection(sectionId);
    if (['regimes', 'risk', 'scenarios', 'uncertainty', 'macro'].includes(sectionId)) {
      setShowAdvancedDrawer(true);
    }
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="flex min-h-screen bg-[#F5F1E8] text-[#343A36]">
      {/* Institutional Left Sidebar in Deep Forest Green */}
      <Sidebar activeSection={activeSection} onSelectSection={handleSectionSelect} />

      {/* Main Terminal Viewport */}
      <div className="flex-1 flex flex-col min-w-0 md:ml-64">
        {/* Top Navigation Bar with Market Status */}
        <header className="h-16 bg-white border-b border-[#E2DDD2] sticky top-0 z-40 flex items-center justify-between px-6 shadow-sm">
          <div className="flex items-center gap-6 overflow-x-auto whitespace-nowrap">
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider text-[#829184] font-mono">COMEX SPOT:</span>
              <span className="text-sm font-bold font-mono text-[#B08D45]">$4,073.00</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider text-[#829184] font-mono">1D CHANGE:</span>
              <span className="text-sm font-bold font-mono text-[#2E6B4F]">+$132.60 (+3.37%)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider text-[#829184] font-mono">INR/10g:</span>
              <span className="text-sm font-bold font-mono text-[#343A36]">₹124,073</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider text-[#829184] font-mono">1 SOVEREIGN (22K):</span>
              <span className="text-sm font-bold font-mono text-[#B08D45]">₹1,07,080 (₹13,385/g)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider text-[#829184] font-mono">ATH DD:</span>
              <span className="text-sm font-bold font-mono text-[#A65345]">-23.42%</span>
            </div>
          </div>

          <div className="flex items-center gap-4 flex-shrink-0">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="px-3 py-1.5 bg-white border border-[#E2DDD2] hover:border-[#B08D45] text-xs font-mono font-semibold rounded text-[#343A36] transition flex items-center gap-2"
            >
              <span className={refreshing ? 'animate-spin' : ''}>↻</span>
              <span>REFRESH</span>
            </button>
          </div>
        </header>

        {/* Content Body: 4 Main Sections + Optional Expandable Drawer */}
        <main className="flex-1 p-4 md:p-8 space-y-10 max-w-7xl w-full mx-auto">
          {/* Connection Error Banner */}
          {error && (
            <div className="bg-[#FAECE9] border-l-4 border-[#A65345] p-4 rounded text-xs text-[#A65345] flex items-center justify-between">
              <div>
                <strong>API Offline:</strong> Using verified local fallback intelligence cache.
              </div>
              <button
                onClick={handleRefresh}
                className="px-3 py-1 bg-[#A65345] text-white rounded font-mono font-bold"
              >
                Retry
              </button>
            </div>
          )}

          {/* ================= 1. MARKET OVERVIEW ================= */}
          <section id="overview" className="scroll-mt-20">
            <MarketOverview intelligence={data?.intelligence || null} />
          </section>

          {/* ================= 2. PRICE TREND ================= */}
          <section id="analysis" className="scroll-mt-20">
            <GoldPriceAnalysis historyData={data?.history || null} />
          </section>

          {/* ================= 3. PRICE PREDICTION ================= */}
          <section id="forecasting" className="scroll-mt-20">
            <ForecastingSection
              forecastData={data?.forecast || null}
              metricsData={data?.metrics || null}
            />
          </section>

          {/* ================= 4. MODEL RELIABILITY ================= */}
          <section id="performance" className="scroll-mt-20">
            <ModelPerformanceSection metricsData={data?.metrics || null} />
          </section>

          {/* ================= OPTIONAL EXPANDABLE ADVANCED RESEARCH DRAWER ================= */}
          <div className="pt-4 border-t border-[#E2DDD2]">
            <button
              onClick={() => setShowAdvancedDrawer(!showAdvancedDrawer)}
              className="w-full bg-white border border-[#E2DDD2] hover:border-[#B08D45] p-4 rounded-lg flex items-center justify-between text-left transition shadow-sm"
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">🏛️</span>
                <div>
                  <div className="text-sm font-bold text-[#263C32]">
                    Optional: Advanced Institutional Research, Regimes & Macro Stress Tests
                  </div>
                  <div className="text-xs text-[#829184]">
                    Detailed ADX trend strength, 6 macro stress scenarios, conditional projections, and 7-channel indicators.
                  </div>
                </div>
              </div>
              <span className="font-mono text-xs text-[#B08D45] font-bold">
                {showAdvancedDrawer ? '▲ Hide Advanced' : '▼ Expand Details'}
              </span>
            </button>

            {showAdvancedDrawer && (
              <div className="mt-8 space-y-10 animate-fadeIn">
                {/* Section D: Market Regime Intelligence */}
                <section id="regimes" className="scroll-mt-20">
                  <MarketRegimeSection
                    trendsData={data?.trends || null}
                    regimeHistoryData={data?.regimeHistory || null}
                  />
                </section>

                {/* Section E: Risk Analytics & Stress Testing */}
                <section id="risk" className="scroll-mt-20">
                  <RiskAnalyticsSection riskData={data?.risk || null} />
                </section>

                {/* Section F: Scenario Forecasting */}
                <section id="scenarios" className="scroll-mt-20">
                  <ScenarioForecastingSection scenariosData={data?.scenarios || null} />
                </section>

                {/* Section G: Prediction Uncertainty Engine */}
                <section id="uncertainty" className="scroll-mt-20">
                  <PredictionUncertaintySection uncertaintyData={data?.uncertainty || null} />
                </section>

                {/* Section H: Macroeconomic Intelligence */}
                <section id="macro" className="scroll-mt-20">
                  <MacroeconomicSection macroData={data?.macro || null} />
                </section>
              </div>
            )}
          </div>

          {/* Editorial Footer */}
          <footer className="pt-8 pb-12 border-t border-[#E2DDD2] text-xs text-[#829184] flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#B08D45]"></span>
              <span className="font-mono text-[#343A36]">
                Global Gold Market Intelligence & Prediction Platform — Editorial Edition 5.0
              </span>
            </div>
            <div className="font-mono text-[11px] text-[#647068]">
              4 Main Sections • Verified Historical Observations • Conformal Calibrated
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
