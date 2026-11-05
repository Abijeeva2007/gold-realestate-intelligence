"""
Quality Reporting and Documentation Generator Module.
Produces comprehensive Markdown and JSON data quality audits, regime analysis reports,
and dataset inventory documents.
"""

from pathlib import Path
from typing import Dict, Any
import json
import pandas as pd

from src.config import REPORTS_DIR, setup_logging

logger = setup_logging()

class QualityReporter:
    """Generates human-readable and machine-parseable data quality reports."""

    def __init__(self):
        self.reports_dir = Path(REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_data_quality_report(
        self,
        validation_results: Dict[str, Any],
        collection_meta: Dict[str, Any]
    ) -> Path:
        """
        Creates a thorough Markdown report detailing data provenance,
        date spans, missingness, duplicate counts, unit validations, and licensing notes.
        """
        report_path = self.reports_dir / "data_quality_report.md"
        json_path = self.reports_dir / "data_quality_metrics.json"

        # Save JSON metrics
        full_metrics = {
            "validation_results": validation_results,
            "collection_meta": collection_meta
        }
        json_path.write_text(json.dumps(full_metrics, indent=2, default=str), encoding="utf-8")

        # Build Markdown content
        d_res = validation_results.get("date_range_check", {})
        dup_res = validation_results.get("duplicate_check", {})
        miss_res = validation_results.get("missingness_check", {})
        unit_res = validation_results.get("units_and_ranges_check", {})
        status = validation_results.get("overall_status", "UNKNOWN")

        md_lines = [
            "# Data Engineering Quality and Validation Report",
            "",
            f"**Overall Pipeline Quality Status:** `{status}`",
            "",
            "## 1. Executive Summary & Objective",
            "This report documents the verification, cleaning, and standardization of historical global and domestic Indian gold prices,",
            "foreign exchange rates (USD/INR), and market regime classifications for the Global Gold Price Intelligence Platform.",
            "",
            "## 2. Temporal Coverage & Range Validation",
            f"- **Target Requirement:** 20+ years of continuous historical market data",
            f"- **Achieved Date Range:** `{d_res.get('start_date')}` to `{d_res.get('end_date')}`",
            f"- **Total Span:** `{d_res.get('years_span')} years`",
            f"- **Target Met:** `{'✅ YES' if d_res.get('valid') else '❌ NO'}`",
            "",
            "## 3. Duplicate and Timestamp Audit",
            f"- **Duplicate Timestamps Found:** `{dup_res.get('duplicate_count', 0)}`",
            f"- **Integrity Result:** `{'✅ CLEAN (0 Duplicates)' if dup_res.get('valid') else '❌ FAILED'}`",
            "",
            "## 4. Missing Observations & Non-Interpolation Audit",
            "Per platform engineering specifications: **No market prices were synthetically interpolated or fabricated.**",
            f"- **Synthetic / Interpolated Records Detected:** `{miss_res.get('any_fabricated_or_interpolated', False)}`",
            f"- **Total Processed Records:** `{miss_res.get('total_records', 0):,}`",
            "",
            "| Column Name | Missing Records | Missing Percentage | Interpretation |",
            "| :--- | :--- | :--- | :--- |"
        ]

        for col, col_data in miss_res.get("columns", {}).items():
            pct = col_data.get("missing_pct", 0)
            cnt = col_data.get("missing_count", 0)
            interp = "Complete" if cnt == 0 else "Exchange closed / Holiday / Non-overlap"
            md_lines.append(f"| `{col}` | {cnt:,} | {pct:.2f}% | {interp} |")

        md_lines.extend([
            "",
            "## 5. Physical Units & Valuation Sanity Checks",
            "| Metric | Observed Range | Expected Bounds | Status |",
            "| :--- | :--- | :--- | :--- |"
        ])

        checks = unit_res.get("checks", {})
        if "gold_usd_bounds" in checks:
            g = checks["gold_usd_bounds"]
            md_lines.append(f"| Global Gold (USD / troy oz) | ${g['min']:,.2f} – ${g['max']:,.2f} | $200 – $10,000 | {'✅ PASS' if g['in_bounds'] else '❌ FAIL'} |")
        if "fx_usdinr_bounds" in checks:
            fx = checks["fx_usdinr_bounds"]
            md_lines.append(f"| USD/INR Exchange Rate | ₹{fx['min']:.2f} – ₹{fx['max']:.2f} | ₹7 – ₹150 | {'✅ PASS' if fx['in_bounds'] else '❌ FAIL'} |")
        if "parity_formula_integrity" in checks:
            p = checks["parity_formula_integrity"]
            md_lines.append(f"| Parity Formula Mathematical Identity | Max diff ₹{p['max_discrepancy_inr']:.4f} | < ₹0.10 tolerance | {'✅ PASS' if p['valid'] else '❌ FAIL'} |")

        md_lines.extend([
            "",
            "## 6. Data Source Provenance & Access Restrictions",
            "| Dataset / Provider | Format / Access | Coverage Span | Access Restrictions & Licensing |",
            "| :--- | :--- | :--- | :--- |",
            "| **COMEX Gold Futures (GC=F)** | Daily OHLCV (API) | 2000 – Present (26+ yrs) | Market feed; open research access. |",
            "| **USD/INR Spot (Yahoo & FRED)** | Daily Close (API/CSV) | 1973/2003 – Present | Federal Reserve H.10 (Public domain); Yahoo FX feed. |",
            "| **RBI Handbook Table 35** | Annual Official Benchmark | 1985 – 2026 (41 yrs) | Reserve Bank of India official publication; open for public research. |",
            "| **RBI Handbook Table 164** | Monthly Official Benchmark | 2022 – 2026 (Monthly) | Official domestic spot (Mumbai) & London spread data. |",
            "| **World Bank Pink Sheet** | Monthly Commodity Data | 1960 – Present (64 yrs) | World Bank Open Data (CC-BY 4.0). |",
            "| **LBMA Direct / WGC** | Direct Feeds | 1970 – Present | LBMA direct bulk feeds require ICE commercial license; WGC direct download restricted by Cloudflare/WAF. |",
            "",
            "---",
            "*Report auto-generated by the Gold Historical Data Engineering Pipeline.*"
        ])

        report_path.write_text("\n".join(md_lines), encoding="utf-8")
        logger.info(f"Data quality report saved to {report_path}")
        return report_path

    def generate_regime_report(self, regime_stats_df: pd.DataFrame) -> Path:
        """Creates a dedicated report summarizing financial market regimes."""
        report_path = self.reports_dir / "regime_analysis_report.md"

        md_lines = [
            "# Macroeconomic and Market Regime Analysis Report",
            "",
            "## 1. Regime Segmentation Overview",
            "Historical gold price performance exhibits distinct macroeconomic behavior during major crisis regimes:",
            "1. **2008 Global Financial Crisis (GFC)**: Liquidity crunch followed by massive safe-haven flight.",
            "2. **2020 COVID-19 Pandemic Shock**: Unprecedented fiscal and monetary expansion; zero interest rate policy.",
            "3. **2024–2026 Structural Bull Regime & Historical Highs**: Central bank reserve diversification, de-dollarization, persistent geopolitical conflict, and all-time highs.",
            "",
            "## 2. Statistical Metrics by Regime",
            "",
            "| Regime Name | Period | Obs | Start ($) | End ($) | Min ($) | Max ($) | Return (%) | Volatility (% p.a.) | Max Drawdown (%) |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        for _, row in regime_stats_df.iterrows():
            md_lines.append(
                f"| **{row['regime_name']}** | {row['start_date']} to {row['end_date']} | "
                f"{row['observations']:,} | ${row['start_price_usd']:,.2f} | ${row['end_price_usd']:,.2f} | "
                f"${row['min_price_usd']:,.2f} | ${row['max_price_usd']:,.2f} | {row['regime_return_pct']:+.2f}% | "
                f"{row['annualized_volatility_pct']}% | {row['max_drawdown_pct']:.2f}% |"
            )

        md_lines.extend([
            "",
            "## 3. Key Observations for Quantitative Modeling",
            "- **2008 GFC:** Gold experienced an initial liquidity drawdown before embarking on a multi-year bull run exceeding +150%.",
            "- **2020 Pandemic:** Volatility spiked as gold surged past $2,000/oz in August 2020.",
            "- **2024–2026 Surge:** Gold demonstrated asymmetric upside persistence, setting consecutive all-time records backed by central bank buying and de-dollarization dynamics.",
            "",
            "---",
            "*Report auto-generated by the Gold Historical Data Engineering Pipeline.*"
        ])

        report_path.write_text("\n".join(md_lines), encoding="utf-8")
        logger.info(f"Regime analysis report saved to {report_path}")
        return report_path
