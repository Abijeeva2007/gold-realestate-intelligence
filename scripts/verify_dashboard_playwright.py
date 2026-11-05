"""
verify_dashboard_playwright.py — Multi-viewport Playwright Acceptance Test Suite
for Task 05 Simplified Gold Price Trend Analysis & Prediction Dashboard.
"""

import os
from playwright.sync_api import sync_playwright

VIEWPORTS = [
    {"name": "desktop_1440x900", "width": 1440, "height": 900},
    {"name": "laptop_1280x800", "width": 1280, "height": 800},
    {"name": "tablet_landscape_1024x768", "width": 1024, "height": 768},
    {"name": "tablet_portrait_768x1024", "width": 768, "height": 1024},
    {"name": "mobile_390x844", "width": 390, "height": 844},
]

DASHBOARD_FILE = "file://" + os.path.abspath("src/dashboard/index.html")
SCREENSHOT_DIR = "data/reports/screenshots"

def run_responsive_audit():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            context = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = context.new_page()

            console_errors = []
            page_errors = []
            page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: page_errors.append(str(e)))

            page.goto(DASHBOARD_FILE)
            page.wait_for_timeout(1000)

            # Check that the 4 main sections exist and are visible
            main_sections = ["overview", "analysis", "forecasting", "performance"]
            found_main = {sec: page.is_visible(f"#{sec}") for sec in main_sections}

            # Check canvases
            canvases = page.eval_on_selector_all(
                "canvas",
                "els => els.map(e => ({id: e.id, width: e.width, height: e.height, visible: e.clientWidth > 0 && e.clientHeight > 0}))"
            )

            # Test Range filters on main historical chart
            page.locator("button:has-text('3M')").click()
            page.wait_for_timeout(200)
            page.locator("button:has-text('1Y')").click()
            page.wait_for_timeout(200)

            # Test Forecast horizon filter
            page.locator("button:has-text('90 Days')").click()
            page.wait_for_timeout(200)
            page.locator("button:has-text('30 Days')").click()
            page.wait_for_timeout(200)

            # Test Expandable Drawer toggle
            drawer_btn = page.locator("#accordionToggleBtn")
            drawer_btn.click()
            page.wait_for_timeout(200)
            is_drawer_open = page.evaluate("document.getElementById('advancedDrawer').classList.contains('open')")

            # Capture screenshot
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"task05_{vp['name']}.png")
            page.screenshot(path=screenshot_path, full_page=True)

            results[vp["name"]] = {
                "viewport": f"{vp['width']}x{vp['height']}",
                "console_errors": len(console_errors),
                "page_errors": len(page_errors),
                "all_main_sections_visible": all(found_main.values()),
                "canvases_rendering": len(canvases) >= 2 and all(c["visible"] for c in canvases),
                "drawer_toggle_functional": is_drawer_open,
                "screenshot": screenshot_path,
            }

            context.close()

        browser.close()

    print("\n--- PLAYWRIGHT RESPONSIVE AUDIT RESULTS (TASK 05) ---")
    all_passed = True
    for name, r in results.items():
        status = "PASS" if (
            r["console_errors"] == 0 
            and r["page_errors"] == 0 
            and r["all_main_sections_visible"] 
            and r["canvases_rendering"] 
            and r["drawer_toggle_functional"]
        ) else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"[{status}] {name} ({r['viewport']}): MainSections={r['all_main_sections_visible']}, Canvases={r['canvases_rendering']}, Errors={r['console_errors']}, Drawer={r['drawer_toggle_functional']}")

    return all_passed

if __name__ == "__main__":
    success = run_responsive_audit()
    exit(0 if success else 1)
