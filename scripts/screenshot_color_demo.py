"""三大icon+hero配色demo截圖(手機優先+桌機參考)，供 user 比較 Demo A(局部金色點綴) / Demo B(整站深色)"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEMO_DIR = ROOT / "samples" / "hero_color_demo"
OUT_DIR = DEMO_DIR

VARIANTS = ["variant-a-gold-accent.html", "variant-b-dark-theme.html"]
VIEWPORTS = {
    "mobile": {"width": 390, "height": 844},
    "desktop": {"width": 1440, "height": 900},
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    for variant in VARIANTS:
        file_url = (DEMO_DIR / variant).as_uri()
        name = variant.replace(".html", "")
        for vp_name, vp in VIEWPORTS.items():
            page = browser.new_page(viewport=vp)
            page.goto(file_url)
            page.wait_for_timeout(300)
            out_path = OUT_DIR / f"{name}_{vp_name}.png"
            page.screenshot(path=str(out_path), full_page=True)
            print(f"saved: {out_path}")
            page.close()
    browser.close()
