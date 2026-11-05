import re
from pathlib import Path

# Reload the clean build_simplified_dashboard.py before failed replacement
builder_path = Path("scripts/build_simplified_dashboard.py")
content = builder_path.read_text(encoding="utf-8")

# If calc_js was added with single braces, remove it or double the braces
content = re.sub(r"\n        // Interactive Jewellery Calculator[\s\S]*?window\.addEventListener\('DOMContentLoaded', updateJewelleryCalc\);\n", "", content)

# Check if substitutions already happened
if "TN 1 SOVEREIGN (22K)" not in content:
    # 1. Update Topnav Ticker
    ticker_old = """                    <div class="ticker-node">
                        <span class="ticker-key">1 SOVEREIGN (8g 22K):</span>
                        <span class="ticker-val" style="color: var(--accent-gold);">₹90,987</span>
                    </div>"""

    ticker_new = """                    <div class="ticker-node" style="background: rgba(176, 141, 69, 0.15); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--accent-gold);">
                        <span class="ticker-key" style="color: var(--accent-gold); font-weight: 700;">TN 1 SOVEREIGN (22K):</span>
                        <span class="ticker-val" style="color: var(--accent-green); font-weight: 700;">₹1,07,080 (₹13,385/g)</span>
                    </div>
                    <div class="ticker-node">
                        <span class="ticker-key">TN 24K (10g):</span>
                        <span class="ticker-val" style="font-weight: 600;">₹1,46,020</span>
                    </div>
                    <div class="ticker-node">
                        <span class="ticker-key">IMPORT PARITY (Ex-Duty):</span>
                        <span class="ticker-val" style="color: var(--text-secondary);">₹124,073 (24K/10g) | ₹90,987 (1 Sov)</span>
                    </div>"""

    content = content.replace(ticker_old, ticker_new)

# Add escaped javascript for calculator
calc_js_escaped = """
        // Interactive Jewellery Calculator
        function setCalcSov(val) {{
            document.getElementById('calcSovereignInput').value = val;
            updateJewelleryCalc();
        }}

        function updateJewelleryCalc() {{
            var sovInput = document.getElementById('calcSovereignInput');
            if (!sovInput) return;
            var sov = parseFloat(sovInput.value) || 1;
            if (sov <= 0) sov = 1;
            
            var vaSelect = document.getElementById('calcVaSelect');
            var vaPct = vaSelect ? (parseFloat(vaSelect.value) || 10) : 10;
            
            var grams = sov * 8.0;
            var gramsText = document.getElementById('calcGramsText');
            if (gramsText) gramsText.innerText = '= ' + grams.toFixed(1) + ' grams';
            
            var ratePerGram = 13385; // Tamil Nadu 22K Ground Reality Benchmark
            var baseGold = Math.round(grams * ratePerGram);
            var making = Math.round(baseGold * (vaPct / 100));
            var gst = Math.round((baseGold + making) * 0.03);
            var grandTotal = baseGold + making + gst;
            
            // 90-day future impact (+4.58%)
            var future90Grand = Math.round(grandTotal * 1.0458);
            var future90Diff = future90Grand - grandTotal;
            
            var baseEl = document.getElementById('calcBaseGoldVal');
            if (baseEl) baseEl.innerText = '₹' + baseGold.toLocaleString('en-IN');
            var makeEl = document.getElementById('calcMakingVal');
            if (makeEl) makeEl.innerText = '₹' + making.toLocaleString('en-IN');
            var gstEl = document.getElementById('calcGstVal');
            if (gstEl) gstEl.innerText = '₹' + gst.toLocaleString('en-IN');
            var grandEl = document.getElementById('calcGrandTotalVal');
            if (grandEl) grandEl.innerText = '₹' + grandTotal.toLocaleString('en-IN');
            var futEl = document.getElementById('calcFuture90Diff');
            if (futEl) futEl.innerText = '+₹' + future90Diff.toLocaleString('en-IN') + ' more';
        }}
        window.addEventListener('DOMContentLoaded', updateJewelleryCalc);
"""

# Insert calc_js_escaped right before closing </script>
content = content.replace("    </script>\n</body>", calc_js_escaped + "\n    </script>\n</body>")

builder_path.write_text(content, encoding="utf-8")
print("Successfully fixed scripts/build_simplified_dashboard.py")
