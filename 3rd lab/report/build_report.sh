#!/usr/bin/env bash
set -euo pipefail

report_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(dirname "$report_dir")"
notebook="$lab_dir/ЛР3_Михальчук_Антон.ipynb"
output_dir="$report_dir/out"
final_pdf="$report_dir/Звіт 3 Михальчука Антона.pdf"

mkdir -p "$output_dir"
XDG_CACHE_HOME=/tmp/uv-cache uv run --with nbconvert \
  jupyter nbconvert --to html --HTMLExporter.embed_images=True \
  --output-dir "$output_dir" --output notebook "$notebook"

"$report_dir/../../../../.venv/bin/python" "$report_dir/render_notebook.py"
python3 /home/serpanok/.codex/skills/lviv-polytechnic-latex-report/scripts/render_report.py "$report_dir/report.tex"
pdfunite "$output_dir/report.pdf" "$output_dir/notebook.pdf" "$final_pdf"
rm -f "$report_dir/report.pdf"
