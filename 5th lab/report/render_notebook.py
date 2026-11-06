"""Print a rendered Jupyter HTML export to an A4 PDF with Chromium."""

import base64
from pathlib import Path

from playwright.sync_api import sync_playwright


REPORT_DIR = Path(__file__).parent
HTML = REPORT_DIR / "out" / "notebook.html"
PDF = REPORT_DIR / "out" / "notebook.pdf"
MAP_HTML = REPORT_DIR.parent / "lr5_маршрут.html"
MAP_PNG = REPORT_DIR / "out" / "map.png"
CHROMIUM = Path("/opt/google/chrome/chrome")


def main() -> None:
    if not HTML.is_file():
        raise FileNotFoundError(f"Missing notebook HTML export: {HTML}")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(CHROMIUM), headless=True)
        page = browser.new_page()
        page.goto(HTML.as_uri(), wait_until="networkidle")
        page.add_style_tag(content="""
            @page { size: A4; margin: 12mm; }
            body { background: white !important; }
            .jp-OutputArea-output, .output_area { overflow: visible !important; }
            table.dataframe { font-size: 8pt; }
            pre, .highlight pre, .jp-InputArea-editor pre {
                white-space: pre-wrap !important;
                overflow-wrap: anywhere !important;
                word-break: break-word !important;
            }
        """)
        # Folium-карта в iframe у друці з'їжджає в кут (iframe отримує розмір пізніше,
        # ніж Leaflet вписує маршрут). Тому знімаємо збережену карту окремо у вікні
        # потрібного розміру і підставляємо в PDF картинку замість iframe.
        map_page = browser.new_page(viewport={"width": 1200, "height": 720},
                                    device_scale_factor=2)
        map_page.goto(MAP_HTML.as_uri(), wait_until="networkidle")
        map_page.wait_for_timeout(3000)
        map_page.screenshot(path=str(MAP_PNG))
        map_page.close()
        png_b64 = base64.b64encode(MAP_PNG.read_bytes()).decode()
        page.evaluate("""(src) => {
            for (const f of document.querySelectorAll('iframe')) {
                const box = f.parentElement.parentElement;   // div width:100% навколо карти
                const img = document.createElement('img');
                img.src = 'data:image/png;base64,' + src;
                img.style.width = '100%';
                box.replaceWith(img);
            }
        }""", png_b64)
        page.emulate_media(media="print")
        page.wait_for_timeout(3000)
        page.wait_for_load_state("networkidle")
        page.pdf(path=str(PDF), format="A4", print_background=True,
                 margin={"top": "12mm", "right": "12mm", "bottom": "12mm", "left": "12mm"})
        browser.close()


if __name__ == "__main__":
    main()
