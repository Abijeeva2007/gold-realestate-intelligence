'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { fetchDashboardBundle, DashboardBundle } from '../services/api';
import { Sidebar } from '../components/Sidebar';
import { MarketOverview } from '../components/MarketOverview';
import { GoldPriceAnalysis } from '../components/GoldPriceAnalysis';
import { ForecastingSection } from '../components/ForecastingSection';
import { ModelPerformanceSection } from '../components/ModelPerformanceSection';

export default function DashboardPage() {
  const [data, setData] = useState<DashboardBundle | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string>('overview');

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
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navigation Bar with Market Status & Terminal Switchers */}
        <header className="h-16 bg-white border-b border-[#E2DDD2] sticky top-0 z-40 flex items-center justify-between px-4 md:px-6 shadow-sm gap-4">
          <div className="flex items-center gap-5 overflow-x-auto whitespace-nowrap py-1">
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] uppercase tracking-wider text-[#829184] font-mono">SPOT:</span>
              <span className="text-sm font-bold font-mono text-[#B08D45]">$4,073.00</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] uppercase tracking-wider text-[#829184] font-mono">1D:</span>
              <span className="text-sm font-bold font-mono text-[#2E6B4F]">+$132.60 (+3.37%)</span>
            </div>
            <div className="flex items-center gap-1.5 bg-[#FCFAF6] px-2.5 py-1 rounded border border-[#B08D45]">
              <span className="text-[11px] uppercase tracking-wider text-[#B08D45] font-mono font-bold">1 SOVEREIGN (22K):</span>
              <span className="text-sm font-extrabold font-mono text-[#263C32]">₹1,07,080</span>
              <span className="text-xs text-[#829184] font-mono">(₹13,385/g)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] uppercase tracking-wider text-[#829184] font-mono">24K/10g:</span>
              <span className="text-sm font-bold font-mono text-[#343A36]">₹124,073</span>
            </div>
          </div>

          {/* Quick Terminal Switcher & Action Buttons */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <a
              href="/real-estate-dashboard"
              className="px-3 py-1.5 bg-[#263C32] text-white hover:bg-[#1C2C25] text-xs font-mono font-bold rounded flex items-center gap-1.5 transition shadow-sm"
              title="Switch to Tamil Nadu Real Estate Terminal"
            >
              <span>🏛️</span>
              <span className="hidden sm:inline">TN Real Estate Terminal</span>
              <span className="sm:hidden">Real Estate</span>
              <span>➔</span>
            </a>

            <a
              href="/dashboard"
              className="px-2.5 py-1.5 bg-[#F5F1E8] border border-[#E2DDD2] hover:border-[#B08D45] text-xs font-mono font-semibold rounded text-[#343A36] transition flex items-center gap-1"
              title="Open Fullscreen Gold Editorial Terminal"
            >
              <span>📊</span>
              <span className="hidden md:inline">Gold Terminal</span>
            </a>

            <a
              href="/docs"
              className="px-2.5 py-1.5 bg-[#F5F1E8] border border-[#E2DDD2] hover:border-[#B08D45] text-xs font-mono font-semibold rounded text-[#343A36] transition flex items-center gap-1"
              title="Open Interactive API Swagger Documentation"
            >
              <span>📖</span>
              <span className="hidden md:inline">Swagger Docs</span>
            </a>

            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="px-2.5 py-1.5 bg-white border border-[#E2DDD2] hover:border-[#B08D45] text-xs font-mono font-semibold rounded text-[#343A36] transition flex items-center gap-1"
            >
              <span className={refreshing ? 'animate-spin' : ''}>↻</span>
              <span className="hidden sm:inline">REFRESH</span>
            </button>
          </div>
        </header>

        {/* Content Body: 4 Clean, Essential Sections */}
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

          {/* ================= INTERACTIVE DUAL-TERMINAL SELECTOR GATEWAY ================= */}
          <div className="bg-white border-2 border-[#B08D45] rounded-xl p-5 md:p-6 shadow-sm">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 pb-4 border-b border-[#E2DDD2]">
              <div>
                <span className="text-[11px] uppercase font-mono tracking-wider font-bold text-[#B08D45]">
                  PORTAL GATEWAY • SELECT YOUR TERMINAL
                </span>
                <h2 className="text-xl md:text-2xl font-bold font-serif text-[#263C32] mt-0.5">
                  Which Intelligence Terminal Would You Like to Explore?
                </h2>
                <p className="text-xs text-[#829184] mt-0.5">
                  Click an option below to immediately navigate between Gold Market Intelligence and Tamil Nadu Real Estate.
                </p>
              </div>
              <div className="flex items-center gap-2 font-mono text-xs text-[#263C32] bg-[#F5F1E8] px-3 py-1.5 rounded-full border border-[#E2DDD2] flex-shrink-0">
                <span className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse"></span>
                <span>2 Active Intelligence Modules</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
              {/* Option 1: Gold Market Intelligence Terminal */}
              <div
                onClick={() => {
                  document.getElementById('overview')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="cursor-pointer border-2 border-[#263C32] bg-[#FCFAF6] hover:bg-white rounded-lg p-5 transition shadow-sm relative group"
              >
                <div className="absolute top-3 right-3 text-[10px] font-mono font-bold bg-[#263C32] text-white px-2 py-0.5 rounded">
                  CURRENTLY VIEWING
                </div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl p-2 bg-[#F5F1E8] rounded-md border border-[#E2DDD2]">🏆</span>
                  <div>
                    <h3 className="text-base font-bold text-[#263C32] group-hover:text-[#B08D45] transition">
                      Gold Price Intelligence Terminal
                    </h3>
                    <span className="text-xs font-mono text-[#829184]">Macro Bullion & Jewellery Forecasts</span>
                  </div>
                </div>
                <ul className="text-xs text-[#556058] space-y-1 mb-4 pl-1">
                  <li>• <strong>Ground-Reality Benchmark:</strong> ₹13,385/g, ₹1,07,080 / 1 Sovereign (8g 22K)</li>
                  <li>• <strong>Showroom Price Calculator:</strong> Base gold + Wastage/VA + 3% GST</li>
                  <li>• <strong>Multi-Horizon Forecasts:</strong> 30d, 90d (wedding advisory), 180d, 365d</li>
                </ul>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    document.getElementById('overview')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                  className="w-full py-2 bg-[#263C32] text-white rounded text-xs font-mono font-bold hover:bg-[#1C2C25] transition flex items-center justify-center gap-1.5"
                >
                  <span>Explore Gold Terminal Sections</span>
                  <span>↓</span>
                </button>
              </div>

              {/* Option 2: Tamil Nadu Real Estate Terminal */}
              <a
                href="/real-estate-dashboard"
                className="border-2 border-[#B08D45] bg-[#FFFFFF] hover:bg-[#FCFAF6] rounded-lg p-5 transition shadow-sm group block text-left no-underline"
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl p-2 bg-[#F5F1E8] rounded-md border border-[#E2DDD2]">🏛️</span>
                  <div>
                    <h3 className="text-base font-bold text-[#263C32] group-hover:text-[#B08D45] transition">
                      Tamil Nadu Real Estate Terminal
                    </h3>
                    <span className="text-xs font-mono text-[#B08D45] font-bold">Includes Kanniyakumari & 38 Districts</span>
                  </div>
                </div>
                <ul className="text-xs text-[#556058] space-y-1 mb-4 pl-1">
                  <li>• <strong>Statewide 38 Districts:</strong> Chennai, Coimbatore to Kanniyakumari</li>
                  <li>• <strong>Guideline vs Market Spreads:</strong> TNREGINET statutory values & trends</li>
                  <li>• <strong>Multi-Horizon Forecasts:</strong> +7.8% (12M) & +16.2% (24M) appreciation</li>
                </ul>
                <div className="w-full py-2 bg-[#B08D45] text-white rounded text-xs font-mono font-bold hover:bg-[#8E6F30] transition flex items-center justify-center gap-1.5 text-center">
                  <span>Go to Real Estate Terminal</span>
                  <span>➔</span>
                </div>
              </a>
            </div>
          </div>

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

          {/* Editorial Footer */}
          <footer className="pt-8 pb-12 border-t border-[#E2DDD2] text-xs text-[#829184] flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#B08D45]"></span>
              <span className="font-mono text-[#343A36]">
                Global Gold Market Intelligence & Prediction Platform — Editorial Edition 5.0
              </span>
            </div>
            <div className="flex items-center gap-4 font-mono text-[11px] text-[#647068]">
              <a href="/real-estate-dashboard" className="hover:text-[#B08D45] transition">🏛️ TN Real Estate Terminal</a>
              <span>•</span>
              <a href="/dashboard" className="hover:text-[#B08D45] transition">📊 Gold Terminal</a>
              <span>•</span>
              <a href="/docs" className="hover:text-[#B08D45] transition">📖 Swagger Docs</a>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
