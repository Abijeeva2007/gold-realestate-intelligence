'use client';

import React from 'react';

export default function GatewayPage() {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#F5F1E8',
      color: '#343A36',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Top Header Bar */}
      <header style={{
        backgroundColor: '#263C32',
        color: '#F5F1E8',
        padding: '1rem 1.5rem',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        borderBottom: '1px solid rgba(216,195,150,0.3)'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 900, color: '#B08D45', letterSpacing: '-0.5px' }}>
              Au / RE
            </span>
            <div>
              <h1 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#FFFFFF' }}>
                Global Gold & USA Real Estate Intelligence Platform
              </h1>
              <p style={{ margin: 0, fontSize: '0.75rem', color: '#D8C396', fontFamily: 'monospace' }}>
                Production Intelligence Gateway • Institutional & Empirical Decision Systems
              </p>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            fontFamily: 'monospace',
            fontSize: '0.75rem',
            overflowX: 'auto',
            whiteSpace: 'nowrap'
          }}>
            <div style={{
              backgroundColor: '#1C2C25',
              padding: '0.35rem 0.75rem',
              borderRadius: '4px',
              border: '1px solid rgba(216,195,150,0.3)',
              display: 'flex',
              gap: '0.5rem'
            }}>
              <span style={{ color: '#829184' }}>GOLD SPOT:</span>
              <span style={{ fontWeight: 700, color: '#B08D45' }}>$4,073/oz</span>
            </div>
            <div style={{
              backgroundColor: '#1C2C25',
              padding: '0.35rem 0.75rem',
              borderRadius: '4px',
              border: '1px solid #B08D45',
              display: 'flex',
              gap: '0.5rem'
            }}>
              <span style={{ color: '#D8C396', fontWeight: 700 }}>1 SOVEREIGN:</span>
              <span style={{ fontWeight: 800, color: '#FFFFFF' }}>₹1,07,080</span>
              <span style={{ color: '#829184', fontSize: '0.65rem' }}>(₹13,385/g)</span>
            </div>
            <div style={{
              backgroundColor: '#1C2C25',
              padding: '0.35rem 0.75rem',
              borderRadius: '4px',
              border: '1px solid rgba(216,195,150,0.3)',
              display: 'flex',
              gap: '0.5rem'
            }}>
              <span style={{ color: '#829184' }}>US MEDIAN:</span>
              <span style={{ fontWeight: 700, color: '#2E6B4F' }}>$420,400 (30Y: 6.65%)</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Choice Gateway */}
      <main style={{
        flex: 1,
        maxWidth: '1100px',
        width: '100%',
        margin: '0 auto',
        padding: '2.5rem 1.5rem',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        boxSizing: 'border-box'
      }}>
        {/* Title & Guidance */}
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: '#FCFAF6',
            border: '1px solid #B08D45',
            padding: '0.35rem 0.85rem',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontFamily: 'monospace',
            fontWeight: 700,
            color: '#B08D45',
            marginBottom: '0.75rem'
          }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#2E7D32' }}></span>
            SELECT AN INTELLIGENCE ENGINE
          </div>
          <h2 style={{
            fontSize: '2.25rem',
            fontWeight: 800,
            color: '#263C32',
            margin: '0.25rem 0 0.5rem',
            letterSpacing: '-0.5px'
          }}>
            Which Dashboard Would You Like to Explore?
          </h2>
          <p style={{
            fontSize: '1rem',
            color: '#647068',
            maxWidth: '650px',
            margin: '0 auto',
            lineHeight: 1.5
          }}>
            Choose either the Gold Market Intelligence Terminal or the Tamil Nadu Real Estate Intelligence Terminal below to launch the dedicated platform.
          </p>
        </div>

        {/* Dual Primary Choice Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '2rem',
          marginBottom: '2.5rem'
        }}>
          {/* Card 1: Gold Market Intelligence */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '2px solid #B08D45',
            borderRadius: '16px',
            padding: '2rem',
            boxShadow: '0 4px 12px rgba(0,0,0,0.06)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            position: 'relative',
            boxSizing: 'border-box'
          }}>
            <div style={{
              position: 'absolute',
              top: 0,
              right: 0,
              backgroundColor: '#B08D45',
              color: '#FFFFFF',
              fontSize: '0.7rem',
              fontFamily: 'monospace',
              fontWeight: 700,
              padding: '0.25rem 0.75rem',
              borderBottomLeftRadius: '8px'
            }}>
              SYSTEM LIVE
            </div>

            <div>
              <div style={{
                width: '56px',
                height: '56px',
                backgroundColor: '#F4EEDF',
                border: '1px solid #B08D45',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.75rem',
                marginBottom: '1.25rem'
              }}>
                🏆
              </div>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#263C32', margin: '0 0 0.25rem' }}>
                Gold Price Intelligence Terminal
              </h3>
              <p style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#829184', margin: '0 0 1rem' }}>
                Macro Bullion Trends • Sovereign Benchmarks • Jewellery Calculators
              </p>

              <div style={{
                backgroundColor: '#FAF7F0',
                border: '1px solid #E2DDD2',
                borderRadius: '8px',
                padding: '0.85rem',
                marginBottom: '1.25rem',
                fontSize: '0.8rem',
                color: '#343A36',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.4rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#647068' }}>22K Standard Rate:</span>
                  <span style={{ fontWeight: 700, fontFamily: 'monospace', color: '#263C32' }}>₹13,385 / gram</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#647068' }}>1 Sovereign (8g 22K):</span>
                  <span style={{ fontWeight: 800, fontFamily: 'monospace', color: '#B08D45' }}>₹1,07,080</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#647068' }}>90-Day Outlook:</span>
                  <span style={{ fontWeight: 700, fontFamily: 'monospace', color: '#2E6B4F' }}>Bullish (+4.58%)</span>
                </div>
              </div>

              <ul style={{
                fontSize: '0.8rem',
                color: '#556058',
                paddingLeft: 0,
                listStyle: 'none',
                margin: '0 0 1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <li style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: '#B08D45', fontWeight: 'bold' }}>✓</span>
                  <span><strong>Historical Trend Charts:</strong> 2000–2026 daily series with 1M, 3M, 6M, 1Y, and MAX filters.</span>
                </li>
                <li style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: '#B08D45', fontWeight: 'bold' }}>✓</span>
                  <span><strong>Showroom Price Calculator:</strong> 22K gold, custom wastage (8%–14%), and 3% GST.</span>
                </li>
                <li style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: '#B08D45', fontWeight: 'bold' }}>✓</span>
                  <span><strong>Multi-Horizon Forecasts:</strong> 30d, 90d (wedding advisory), 180d, and 365d predictions.</span>
                </li>
                <li style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: '#B08D45', fontWeight: 'bold' }}>✓</span>
                  <span><strong>Walk-Forward Reliability:</strong> Backtested accuracy scorecard (MAE $220.18, 71.7% dir. acc).</span>
                </li>
              </ul>
            </div>

            <a
              href="/dashboard"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                width: '100%',
                padding: '0.85rem',
                backgroundColor: '#263C32',
                color: '#FFFFFF',
                fontFamily: 'monospace',
                fontWeight: 700,
                fontSize: '0.875rem',
                borderRadius: '8px',
                textDecoration: 'none',
                boxSizing: 'border-box',
                transition: 'background-color 0.2s',
                textAlign: 'center'
              }}
            >
              <span>Launch Gold Intelligence Terminal</span>
              <span>➔</span>
            </a>
          </div>

          {/* Card 2: USA Real Estate Intelligence */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '2px solid #1E2D3D',
            borderRadius: '16px',
            padding: '2rem',
            boxShadow: '0 4px 12px rgba(0,0,0,0.06)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            position: 'relative',
            boxSizing: 'border-box'
          }}>
            <div style={{
              position: 'absolute',
              top: 0,
              right: 0,
              backgroundColor: '#1E2D3D',
              color: '#FFFFFF',
              fontSize: '0.7rem',
              fontFamily: 'monospace',
              fontWeight: 700,
              padding: '0.25rem 0.75rem',
              borderBottomLeftRadius: '8px'
            }}>
              FRED • CASE-SHILLER • NAR
            </div>

            <div>
              <div style={{
                width: '56px',
                height: '56px',
                backgroundColor: '#EBF2F8',
                border: '1px solid #1B4D7E',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.75rem',
                marginBottom: '1.25rem'
              }}>
                🇺🇸
              </div>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#1E2D3D', margin: '0 0 0.25rem' }}>
                USA Real Estate Intelligence Terminal
              </h3>
              <p style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#829184', margin: '0 0 1rem' }}>
                Case-Shiller Home Price Index • Top 20 Metros • PITI Mortgage & Forecasts
              </p>

              <div style={{
                backgroundColor: '#FAF7F0',
                border: '1px solid #E2DDD2',
                borderRadius: '8px',
                padding: '0.85rem',
                marginBottom: '1.25rem',
                fontSize: '0.8rem',
                color: '#343A36',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.4rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#647068' }}>US Median Home Price:</span>
                  <span style={{ fontWeight: 700, fontFamily: 'monospace', color: '#1E2D3D' }}>$420,400 ($228/sq.ft)</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#647068' }}>12-Month Price Projection:</span>
                  <span style={{ fontWeight: 800, fontFamily: 'monospace', color: '#2E6B4F' }}>+4.6% Growth</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#647068' }}>30-Year Fixed Mortgage:</span>
                  <span style={{ fontWeight: 700, fontFamily: 'monospace', color: '#1B4D7E' }}>6.65% (Eased from 7.79%)</span>
                </div>
              </div>

              <ul style={{
                fontSize: '0.8rem',
                color: '#556058',
                paddingLeft: 0,
                listStyle: 'none',
                margin: '0 0 1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <li style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: '#1B4D7E', fontWeight: 'bold' }}>✓</span>
                  <span><strong>Case-Shiller Trend Charts:</strong> 2015–2026 historical series with 3Y, 5Y, and 10Y filters.</span>
                </li>
                <li style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: '#1B4D7E', fontWeight: 'bold' }}>✓</span>
                  <span><strong>Top 20 US Metro Rankings:</strong> New York, LA, San Francisco, Miami, Austin, Seattle, Dallas, Atlanta.</span>
                </li>
                <li style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: '#1B4D7E', fontWeight: 'bold' }}>✓</span>
                  <span><strong>PITI Mortgage & Valuation Calculator:</strong> Principal, Interest, Property Taxes, Insurance & rental yield.</span>
                </li>
                <li style={{ display: 'flex', gap: '0.5rem' }}>
                  <span style={{ color: '#1B4D7E', fontWeight: 'bold' }}>✓</span>
                  <span><strong>Investment & Cap Rate Advisory:</strong> Sunbelt (5.5%–6.5%) vs Coastal MSAs (3.5%–4.5%).</span>
                </li>
              </ul>
            </div>

            <a
              href="/real-estate-dashboard"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                width: '100%',
                padding: '0.85rem',
                backgroundColor: '#1E2D3D',
                color: '#FFFFFF',
                fontFamily: 'monospace',
                fontWeight: 700,
                fontSize: '0.875rem',
                borderRadius: '8px',
                textDecoration: 'none',
                boxSizing: 'border-box',
                transition: 'background-color 0.2s',
                textAlign: 'center'
              }}
            >
              <span>Launch USA Real Estate Terminal</span>
              <span>➔</span>
            </a>
          </div>
        </div>

        {/* Supplementary Gateway Options: API Documentation */}
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2DDD2',
          borderRadius: '12px',
          padding: '1.25rem 1.5rem',
          boxShadow: '0 2px 4px rgba(0,0,0,0.04)',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              fontSize: '1.5rem',
              padding: '0.5rem 0.75rem',
              backgroundColor: '#FAF7F0',
              border: '1px solid #E2DDD2',
              borderRadius: '8px'
            }}>
              📖
            </div>
            <div>
              <h4 style={{ margin: '0 0 0.25rem', fontSize: '0.95rem', fontWeight: 700, color: '#263C32' }}>
                Interactive API Swagger Documentation
              </h4>
              <p style={{ margin: 0, fontSize: '0.8rem', color: '#829184' }}>
                Explore REST endpoints for Gold prices, historical series, 38-district guideline values, and valuation predictions.
              </p>
            </div>
          </div>
          <a
            href="/docs"
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#FAF7F0',
              border: '1px solid #B08D45',
              color: '#263C32',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontFamily: 'monospace',
              fontWeight: 700,
              textDecoration: 'none',
              whiteSpace: 'nowrap'
            }}
          >
            Open Swagger Docs ➔
          </a>
        </div>
      </main>

      {/* Editorial Footer */}
      <footer style={{
        backgroundColor: '#FFFFFF',
        borderTop: '1px solid #E2DDD2',
        padding: '1.25rem 1.5rem',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: '#829184',
        fontFamily: 'monospace'
      }}>
        <div style={{
          maxWidth: '1100px',
          margin: '0 auto',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '0.5rem'
        }}>
          <span>Gold Price Intelligence & Tamil Nadu Real Estate Platform • Editorial Edition</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <a href="/dashboard" style={{ color: '#647068', textDecoration: 'none' }}>Gold Terminal</a>
            <span>•</span>
            <a href="/real-estate-dashboard" style={{ color: '#647068', textDecoration: 'none' }}>TN Real Estate</a>
            <span>•</span>
            <a href="/docs" style={{ color: '#647068', textDecoration: 'none' }}>API Docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
