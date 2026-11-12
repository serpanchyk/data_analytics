"""Print a rendered Jupyter HTML export to an A4 PDF with Chromium."""

from pathlib import Path

from playwright.sync_api import sync_playwright


REPORT_DIR = Path(__file__).parent
HTML = REPORT_DIR / "out" / "notebook.html"
PDF = REPORT_DIR / "out" / "notebook.pdf"
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
        page.pdf(path=str(PDF), format="A4", print_background=True,
                 margin={"top": "12mm", "right": "12mm", "bottom": "12mm", "left": "12mm"})
        browser.close()


if __name__ == "__main__":
    main()
