"""
Record an application walkthrough video using Playwright (live UI only).

Usage:
  1. Start backend:  cd backend && uvicorn app.main:app --port 8000
  2. Run: python scripts/record_demo.py
"""

import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "demo_recording.webm"
APP_URL = "http://localhost:8000"


def scroll_page(page, steps: int, pause: float = 4.0, amount: int = 220):
    for _ in range(steps):
        page.evaluate(f"window.scrollBy(0, {amount})")
        time.sleep(pause)


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install playwright: pip install playwright && python -m playwright install chromium")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    for f in OUTPUT.parent.glob("*.webm"):
        if f.name != "demo_recording.webm":
            try:
                f.unlink()
            except OSError:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=str(OUTPUT.parent),
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()

        print("Recording application walkthrough…")

        # Dashboard intro
        page.goto(APP_URL, wait_until="networkidle", timeout=60000)
        time.sleep(8)

        # Run full analysis
        btn = page.get_by_role("button", name="Run Full Analysis")
        if btn.is_visible():
            btn.click()
            print("  Running full analysis…")
            time.sleep(18)

        # Walk through dashboard — metrics, chart, competitors, opportunities
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(5)
        scroll_page(page, steps=12, pause=5.0)

        # Query detail
        page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        view_btn = page.locator('button:has-text("View")').first
        if view_btn.count() > 0:
            view_btn.click()
            time.sleep(6)
            scroll_page(page, steps=10, pause=5.0, amount=180)
            page.evaluate("document.getElementById('backBtn')?.click()")
            time.sleep(4)

        # Opportunities + runs list
        page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.55)")
        time.sleep(8)
        scroll_page(page, steps=6, pause=5.0)

        # Second query detail (different run if available)
        runs = page.locator('button:has-text("View")')
        if runs.count() > 1:
            runs.nth(1).click()
            time.sleep(6)
            scroll_page(page, steps=8, pause=5.0, amount=180)
            page.evaluate("document.getElementById('backBtn')?.click()")
            time.sleep(4)

        # Export report
        page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        report_btn = page.get_by_role("button", name="Export Report")
        if report_btn.is_visible():
            report_btn.click()
            time.sleep(10)

        # Final pass over dashboard
        page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        time.sleep(5)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(8)
        scroll_page(page, steps=8, pause=4.5)

        page.screenshot(path=str(OUTPUT.parent / "demo_screenshot_dashboard.png"), full_page=True)

        context.close()
        browser.close()

    videos = sorted(OUTPUT.parent.glob("*.webm"), key=lambda p: p.stat().st_size, reverse=True)
    if videos:
        best = videos[0]
        if best != OUTPUT:
            if OUTPUT.exists():
                OUTPUT.unlink()
            best.rename(OUTPUT)
        size_mb = OUTPUT.stat().st_size / (1024 * 1024)
        print(f"Video saved: {OUTPUT} ({size_mb:.1f} MB)")
    else:
        print("No video file generated.")


if __name__ == "__main__":
    main()
