# Macroeconomic Intelligence — Data Provenance & Point-in-Time Documentation

## 1. Executive Overview
This document establishes the official data dictionary, publication schedules, revision policies, 
and point-in-time integrity guarantees for all 7 global macroeconomic drivers integrated into the 
Gold Investment Intelligence Engine (Task 03).

---

## 2. Macroeconomic Indicator Catalog

| Indicator Key | Full Name | Primary Provider | Cadence | Publication Lag | Latest Reference | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DXY` | **US Dollar Index (DXY)** | ICE / Intercontinental Exchange (Market Feed: DX-Y.NYB) | Daily | Same-day (Real-time / T+0) | `104.38 Index Points (Base 100)` | Active & Verified |
| `US10Y_YIELD` | **US 10-Year Treasury Benchmark Yield** | US Department of the Treasury / CBOE (^TNX) | Daily | Same-day (T+0) | `4.38 Percent per annum (%)` | Active & Verified |
| `US10Y_REAL_YIELD` | **US 10-Year Real Yield (TIPS Yield)** | Federal Reserve Bank of St. Louis (FRED: DFII10) | Daily | T+1 business day dissemination at 8:00 AM EST. | `1.95 Percent per annum (%)` | Active & Verified |
| `US_CPI` | **US Consumer Price Index (Headline CPI - All Urban Consumers)** | US Bureau of Labor Statistics (BLS: CPIAUCSL) | Monthly | Strict publication lag: Released between 10th-14th of month T+1 (Point-in-time strictly enforced). | `315.3 Index (1982-1984=100) & YoY % Change` | Active & Verified |
| `USD_INR` | **USD to Indian Rupee Spot Exchange Rate** | Reserve Bank of India (RBI FBIL Reference Rate) / Yahoo Finance (INR=X) | Daily | Same-day (T+0) | `94.94 INR per 1 USD` | Active & Verified |
| `GOLD_ETF_HOLDINGS` | **Global Gold ETF Holdings (SPDR GLD + iShares IAU)** | State Street Global Advisors (GLD) & BlackRock (IAU) official disclosures | Daily | T+1 morning publication on trust websites. | `1315.2 Metric Tonnes of Physical Gold Bullion` | Active & Verified |
| `CENTRAL_BANK_PURCHASES` | **Official Sector Net Gold Purchases** | World Gold Council (WGC) / IMF International Financial Statistics (IFS) | Quarterly (with monthly partial IMF disclosures) | 45-day reporting lag post quarter-end (Q3 published mid-Nov, Q4 published mid-Feb). | `1037.0 Net Metric Tonnes Purchased` | Active & Verified |

---

## 3. Detailed Data Governance & Point-in-Time Methodology

### US Dollar Index (DXY) (`DXY`)
- **Data Provider:** ICE / Intercontinental Exchange (Market Feed: DX-Y.NYB)
- **Reporting Frequency:** Daily
- **Unit of Measure:** Index Points (Base 100)
- **Observation vs. Publication Timing:** Market Close (T+0) $\rightarrow$ Same-day (Real-time / T+0)
- **Missing Value Handling:** Forward-fill previous business day close during currency market holidays.
- **Revision Policy:** None (Market-settled transactional closing prints).
- **Licensing & Usage Limitations:** Public financial market quotes for non-commercial research.
- **Point-in-Time Enforcement:** Strict zero-look-ahead policy enforced. No future publication dates peek into historical feature rows.

### US 10-Year Treasury Benchmark Yield (`US10Y_YIELD`)
- **Data Provider:** US Department of the Treasury / CBOE (^TNX)
- **Reporting Frequency:** Daily
- **Unit of Measure:** Percent per annum (%)
- **Observation vs. Publication Timing:** Daily 3:30 PM EST $\rightarrow$ Same-day (T+0)
- **Missing Value Handling:** Forward-fill on SIFMA US bond market holidays.
- **Revision Policy:** None (Market closing auction yield).
- **Licensing & Usage Limitations:** Public domain (US Treasury Department market dissemination).
- **Point-in-Time Enforcement:** Strict zero-look-ahead policy enforced. No future publication dates peek into historical feature rows.

### US 10-Year Real Yield (TIPS Yield) (`US10Y_REAL_YIELD`)
- **Data Provider:** Federal Reserve Bank of St. Louis (FRED: DFII10)
- **Reporting Frequency:** Daily
- **Unit of Measure:** Percent per annum (%)
- **Observation vs. Publication Timing:** Daily Business Day $\rightarrow$ T+1 business day dissemination at 8:00 AM EST.
- **Missing Value Handling:** Forward-fill for holidays; linear interpolation prohibited.
- **Revision Policy:** Infrequent Treasury model curve revisions.
- **Licensing & Usage Limitations:** Public domain (Federal Reserve Economic Data).
- **Point-in-Time Enforcement:** Strict zero-look-ahead policy enforced. No future publication dates peek into historical feature rows.

### US Consumer Price Index (Headline CPI - All Urban Consumers) (`US_CPI`)
- **Data Provider:** US Bureau of Labor Statistics (BLS: CPIAUCSL)
- **Reporting Frequency:** Monthly
- **Unit of Measure:** Index (1982-1984=100) & YoY % Change
- **Observation vs. Publication Timing:** Monthly Reference Month $\rightarrow$ Strict publication lag: Released between 10th-14th of month T+1 (Point-in-time strictly enforced).
- **Missing Value Handling:** Step-function forward-fill strictly from publication date forward.
- **Revision Policy:** Annual seasonal factor revisions released each February.
- **Licensing & Usage Limitations:** Public domain (US Bureau of Labor Statistics).
- **Point-in-Time Enforcement:** Strict zero-look-ahead policy enforced. No future publication dates peek into historical feature rows.

### USD to Indian Rupee Spot Exchange Rate (`USD_INR`)
- **Data Provider:** Reserve Bank of India (RBI FBIL Reference Rate) / Yahoo Finance (INR=X)
- **Reporting Frequency:** Daily
- **Unit of Measure:** INR per 1 USD
- **Observation vs. Publication Timing:** Daily 1:30 PM IST (RBI Fixing) / 5:00 PM EST (Market Close) $\rightarrow$ Same-day (T+0)
- **Missing Value Handling:** Forward-fill when Indian or US markets diverge on regional holidays.
- **Revision Policy:** None (Official reference fixing is final).
- **Licensing & Usage Limitations:** Public RBI reference rates & public market feeds.
- **Point-in-Time Enforcement:** Strict zero-look-ahead policy enforced. No future publication dates peek into historical feature rows.

### Global Gold ETF Holdings (SPDR GLD + iShares IAU) (`GOLD_ETF_HOLDINGS`)
- **Data Provider:** State Street Global Advisors (GLD) & BlackRock (IAU) official disclosures
- **Reporting Frequency:** Daily
- **Unit of Measure:** Metric Tonnes of Physical Gold Bullion
- **Observation vs. Publication Timing:** Daily Fund Share Tally $\rightarrow$ T+1 morning publication on trust websites.
- **Missing Value Handling:** Forward-fill on weekends and market holidays.
- **Revision Policy:** None (Physical bullion bar list audits performed semi-annually).
- **Licensing & Usage Limitations:** Public SEC statutory fund filings.
- **Point-in-Time Enforcement:** Strict zero-look-ahead policy enforced. No future publication dates peek into historical feature rows.

### Official Sector Net Gold Purchases (`CENTRAL_BANK_PURCHASES`)
- **Data Provider:** World Gold Council (WGC) / IMF International Financial Statistics (IFS)
- **Reporting Frequency:** Quarterly (with monthly partial IMF disclosures)
- **Unit of Measure:** Net Metric Tonnes Purchased
- **Observation vs. Publication Timing:** Quarterly Calendar Quarter $\rightarrow$ 45-day reporting lag post quarter-end (Q3 published mid-Nov, Q4 published mid-Feb).
- **Missing Value Handling:** Quarterly step-function. Values become available strictly on release date.
- **Revision Policy:** Subject to retrospective updates as sovereign central banks disclose unreported purchases.
- **Licensing & Usage Limitations:** Free public research citation under World Gold Council attribution.
- **Point-in-Time Enforcement:** Strict zero-look-ahead policy enforced. No future publication dates peek into historical feature rows.

---
*Report auto-generated by the Global Gold Intelligence Platform.*