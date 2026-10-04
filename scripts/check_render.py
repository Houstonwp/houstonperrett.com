#!/usr/bin/env python3
"""Browser layout smoke checks against a freshly generated local site."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
import tomllib
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)
BASE = tomllib.loads((ROOT / "config.toml").read_text())["baseURL"]

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "public")))
Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/"
results = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for width in (320, 390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 900})
            response = page.goto(url, wait_until="networkidle")
            assert response.status == 200
            metrics = page.evaluate("""() => ({width: innerWidth,
                documentWidth: document.documentElement.scrollWidth,
                brokenImages: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src)})""")
            page.screenshot(path=str(OUT / f"home-{width}.png"), full_page=True)
            results.append(metrics)
            assert metrics["documentWidth"] <= width, metrics
            assert not metrics["brokenImages"], metrics
        if "resume." in BASE:
            for size in ("Letter", "A4"):
                page.pdf(path=str(OUT / f"resume-{size}.pdf"), format=size,
                         print_background=True, display_header_footer=False,
                         margin={"top": "0.25in", "right": "0.25in", "bottom": "0.25in", "left": "0.25in"})
        if "blog." in BASE:
            page.goto(url + "post/2019-11-03-newsletter/", wait_until="networkidle")
            images = page.locator('img[src^="/images/rework_"]')
            assert images.count() == 4
            assert images.evaluate_all("images => images.every(i => i.complete && i.naturalWidth > 0)")
            page.screenshot(path=str(OUT / "repaired-post-images.png"), full_page=True)
            page.go_back(wait_until="networkidle")
            assert page.url == url
        browser.close()
finally:
    server.shutdown()
    (OUT / "layout-results.json").write_text(json.dumps(results, indent=2))
print("PASS: desktop/mobile layout and available site-specific browser checks")
