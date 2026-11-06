'use client';

import React from 'react';

export default function GatewayPage() {
  return (
    <div className="min-h-screen bg-[#F5F1E8] text-[#343A36] flex flex-col font-sans">
      {/* Top Header Bar */}
      <header className="bg-[#263C32] text-[#F5F1E8] py-4 px-6 shadow-md border-b border-[#D8C396]/30">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-serif font-black text-[#B08D45] tracking-tight">Au / RE</span>
            <div>
              <h1 className="text-base sm:text-lg font-bold font-serif tracking-wide text-white">
                Global Gold & Tamil Nadu Real Estate Intelligence Platform
              </h1>
              <p className="text-[11px] font-mono text-[#D8C396]">
                Production Intelligence Gateway • Institutional & Empirical Decision Systems
              </p>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="flex items-center gap-3 font-mono text-xs overflow-x-auto whitespace-nowrap py-1">
            <div className="bg-[#1C2C25] px-3 py-1.5 rounded border border-[#D8C396]/30 flex items-center gap-2">
              <span className="text-[#829184]">GOLD SPOT:</span>
              <span className="font-bold text-[#B08D45]">$4,073/oz</span>
            </div>
            <div className="bg-[#1C2C25] px-3 py-1.5 rounded border border-[#B08D45] flex items-center gap-2">
              <span className="text-[#D8C396] font-bold">1 SOVEREIGN:</span>
              <span className="font-extrabold text-white">₹1,07,080</span>
              <span className="text-[10px] text-[#829184]">(₹13,385/g)</span>
            </div>
            <div className="bg-[#1C2C25] px-3 py-1.5 rounded border border-[#D8C396]/30 flex items-center gap-2">
              <span className="text-[#829184]">TN DISTRICTS:</span>
              <span className="font-bold text-[#2E6B4F]">38 Complete</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Choice Gateway */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-10 flex flex-col justify-center">
        {/* Title & Guidance */}
        <div className="text-center mb-8 md:mb-12">
          <div className="inline-flex items-center gap-2 bg-[#FCFAF6] border border-[#B08D45] px-3.5 py-1.5 rounded-full text-xs font-mono font-bold text-[#B08D45] mb-3 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse"></span>
            SELECT AN INTELLIGENCE ENGINE
          </div>
          <h2 className="text-3xl md:text-4xl font-extrabold font-serif text-[#263C32] tracking-tight">
            Which Dashboard Would You Like to Explore?
          </h2>
          <p className="text-sm md:text-base text-[#647068] max-w-2xl mx-auto mt-2">
            Choose either the Gold Market Intelligence Terminal or the Tamil Nadu Real Estate Intelligence Terminal below to launch the dedicated platform.
          </p>
        </div>

        {/* Dual Primary Choice Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 mb-10">
          {/* Card 1: Gold Market Intelligence */}
          <div className="bg-white border-2 border-[#B08D45] rounded-2xl p-6 md:p-8 shadow-md hover:shadow-xl transition-all duration-300 flex flex-col justify-between group relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-[#B08D45] text-white text-[11px] font-mono font-bold px-3 py-1 rounded-bl-lg">
              SYSTEM LIVE
            </div>

            <div>
              <div className="w-14 h-14 bg-[#F4EEDF] border border-[#B08D45] rounded-xl flex items-center justify-center text-3xl mb-5 shadow-sm group-hover:scale-105 transition-transform">
                🏆
              </div>
              <h3 className="text-2xl font-bold font-serif text-[#263C32] group-hover:text-[#B08D45] transition-colors">
                Gold Price Intelligence Terminal
              </h3>
              <p className="text-xs font-mono text-[#829184] mt-1 mb-4">
                Macro Bullion Trends • Sovereign Benchmarks • Jewellery Calculators
              </p>

              <div className="bg-[#FAF7F0] border border-[#E2DDD2] rounded-lg p-3.5 mb-5 text-xs text-[#343A36] space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-[#647068]">22K Standard Rate:</span>
                  <span className="font-bold font-mono text-[#263C32]">₹13,385 / gram</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#647068]">1 Sovereign (8g 22K):</span>
                  <span className="font-extrabold font-mono text-[#B08D45]">₹1,07,080</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#647068]">90-Day Outlook:</span>
                  <span className="font-bold font-mono text-[#2E6B4F]">Bullish (+4.58%)</span>
                </div>
              </div>

              <ul className="text-xs text-[#556058] space-y-2 mb-6">
                <li className="flex items-start gap-2">
                  <span className="text-[#B08D45] font-bold">✓</span>
                  <span><strong>Complete Historical Trend Charts:</strong> 2000–2026 daily series with 1M, 3M, 6M, 1Y, and MAX filters.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#B08D45] font-bold">✓</span>
                  <span><strong>Showroom Price Calculator:</strong> Instant breakdown of 22K gold, custom wastage/making charges (8%–14%), and 3% GST.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#B08D45] font-bold">✓</span>
                  <span><strong>Multi-Horizon Forecasting Engine:</strong> 30d, 90d (wedding advisory), 180d, and 365d predictions with confidence intervals.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#B08D45] font-bold">✓</span>
                  <span><strong>Walk-Forward Model Reliability:</strong> Backtested accuracy scorecard with MAE $220.18 and 71.7% directional accuracy.</span>
                </li>
              </ul>
            </div>

            <a
              href="/dashboard"
              className="w-full py-3.5 bg-[#263C32] hover:bg-[#1C2C25] text-white font-mono font-bold text-sm rounded-xl text-center shadow transition-all flex items-center justify-center gap-2 group-hover:bg-[#B08D45]"
            >
              <span>Launch Gold Intelligence Terminal</span>
              <span className="text-base">➔</span>
            </a>
          </div>

          {/* Card 2: Tamil Nadu Real Estate Intelligence */}
          <div className="bg-white border-2 border-[#263C32] rounded-2xl p-6 md:p-8 shadow-md hover:shadow-xl transition-all duration-300 flex flex-col justify-between group relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-[#263C32] text-white text-[11px] font-mono font-bold px-3 py-1 rounded-bl-lg">
              38 DISTRICTS
            </div>

            <div>
              <div className="w-14 h-14 bg-[#EBF3EE] border border-[#263C32] rounded-xl flex items-center justify-center text-3xl mb-5 shadow-sm group-hover:scale-105 transition-transform">
                🏛️
              </div>
              <h3 className="text-2xl font-bold font-serif text-[#263C32] group-hover:text-[#2E6B4F] transition-colors">
                Tamil Nadu Real Estate Terminal
              </h3>
              <p className="text-xs font-mono text-[#829184] mt-1 mb-4">
                Statutory Guideline Values • Market Spreads • Price Predictions & Investment
              </p>

              <div className="bg-[#FAF7F0] border border-[#E2DDD2] rounded-lg p-3.5 mb-5 text-xs text-[#343A36] space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-[#647068]">Geographic Scope:</span>
                  <span className="font-bold font-mono text-[#263C32]">All 38 Districts (incl. Kanniyakumari)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#647068]">12-Month Price Projection:</span>
                  <span className="font-extrabold font-mono text-[#2E6B4F]">+7.8% Growth</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#647068]">Total Investment ROI (CAGR):</span>
                  <span className="font-bold font-mono text-[#B08D45]">11.5% – 12.0%</span>
                </div>
              </div>

              <ul className="text-xs text-[#556058] space-y-2 mb-6">
                <li className="flex items-start gap-2">
                  <span className="text-[#263C32] font-bold">✓</span>
                  <span><strong>Full 38 District Rankings:</strong> Chennai, Coimbatore, Madurai, Tiruchirappalli to Kanniyakumari (Nagercoil, Cape Road).</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#263C32] font-bold">✓</span>
                  <span><strong>Statutory vs Market Spreads:</strong> TNREGINET guideline benchmarks and market transaction multiples.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#263C32] font-bold">✓</span>
                  <span><strong>Real Estate Price Forecasts:</strong> Multi-horizon 12M (+7.8%) and 24M (+16.2%) econometric appreciation projections.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#263C32] font-bold">✓</span>
                  <span><strong>Interactive Valuation Calculator:</strong> Instant sq.ft and total property valuation by locality and asset class.</span>
                </li>
              </ul>
            </div>

            <a
              href="/real-estate-dashboard"
              className="w-full py-3.5 bg-[#263C32] hover:bg-[#1C2C25] text-white font-mono font-bold text-sm rounded-xl text-center shadow transition-all flex items-center justify-center gap-2 group-hover:bg-[#2E6B4F]"
            >
              <span>Launch Real Estate Terminal</span>
              <span className="text-base">➔</span>
            </a>
          </div>
        </div>

        {/* Supplementary Gateway Options: API Documentation */}
        <div className="bg-white border border-[#E2DDD2] rounded-xl p-5 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="text-2xl p-2.5 bg-[#FAF7F0] border border-[#E2DDD2] rounded-lg">
              📖
            </div>
            <div>
              <h4 className="text-sm font-bold text-[#263C32]">Interactive API Swagger Documentation</h4>
              <p className="text-xs text-[#829184]">
                Explore REST endpoints for Gold prices, historical series, 38-district guideline values, and valuation predictions.
              </p>
            </div>
          </div>
          <a
            href="/docs"
            className="px-4 py-2 bg-[#FAF7F0] border border-[#B08D45] text-[#263C32] hover:bg-[#B08D45] hover:text-white rounded-lg text-xs font-mono font-bold transition whitespace-nowrap shadow-sm"
          >
            Open Swagger Docs ➔
          </a>
        </div>
      </main>

      {/* Editorial Footer */}
      <footer className="bg-white border-t border-[#E2DDD2] py-5 px-6 text-center text-xs text-[#829184] font-mono">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Gold Price Intelligence & Tamil Nadu Real Estate Platform • Editorial Edition</span>
          <div className="flex items-center gap-3">
            <a href="/dashboard" className="hover:text-[#B08D45] transition">Gold Terminal</a>
            <span>•</span>
            <a href="/real-estate-dashboard" className="hover:text-[#B08D45] transition">TN Real Estate</a>
            <span>•</span>
            <a href="/docs" className="hover:text-[#B08D45] transition">API Docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
