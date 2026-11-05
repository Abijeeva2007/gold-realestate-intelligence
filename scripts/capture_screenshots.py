import os
import sys
import time
import threading
import uvicorn
from playwright.sync_api import sync_playwright

def run_server():
    from src.api.app import app
    uvicorn.run(app, host="127.0.0.1", port=8899, log_level="warning")

def capture_before_screenshot():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)  # give server time to bind

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        page.goto("http://127.0.0.1:8899/dashboard")
        page.wait_for_timeout(2000)

        os.makedirs("data/reports/screenshots", exist_ok=True)
        page.screenshot(path="data/reports/screenshots/before_desktop_1440x900.png", full_page=True)
        print("Captured data/reports/screenshots/before_desktop_1440x900.png")
        print("Console errors detected:", len(console_errors), console_errors)

        browser.close()

if __name__ == "__main__":
    capture_before_screenshot()
