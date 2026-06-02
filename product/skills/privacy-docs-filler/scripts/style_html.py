#!/usr/bin/env python3
"""
style_html.py — Добавляет CSS-оформление к HTML-файлам, сгенерированным pandoc из .docx.

Использование:
    python3 style_html.py <output_dir> <org_label>
"""

import sys
import re
from pathlib import Path

CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap');

  *, *::before, *::after { box-sizing: border-box; }

  body {
    font-family: 'PT Serif', 'Times New Roman', serif;
    font-size: 14px;
    line-height: 1.7;
    color: #1a1a1a;
    background: #f0f0f0;
    margin: 0;
    padding: 30px 20px;
  }

  .page {
    background: #ffffff;
    max-width: 800px;
    margin: 0 auto;
    padding: 60px 72px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.13);
    border-radius: 2px;
  }

  h1.doc-title {
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    margin: 0 0 20px 0;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  p { margin: 0 0 8px 0; text-align: justify; }

  strong { font-weight: bold; }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 13px;
  }

  th, td {
    border: 1px solid #555;
    padding: 6px 10px;
    text-align: left;
    vertical-align: top;
  }

  th {
    background: #f5f5f5;
    font-weight: bold;
    text-align: center;
  }

  header#title-block-header { display: none; }

  @media print {
    body { background: white; padding: 0; }
    .page { box-shadow: none; padding: 20mm 25mm; max-width: none; }
  }
</style>
"""

DOC_TITLES = [
    "Политика конфиденциальности",
    "Согласие на обработку персональных данных",
    "Пользовательское соглашение",
]


def style_file(path: Path, doc_title: str):
    html = path.read_text(encoding="utf-8")

    html = html.replace("</style>", "</style>" + CSS, 1)

    html = re.sub(r'(<body[^>]*>)', r'\1\n<div class="page">', html)
    html = html.replace("</body>", "</div>\n</body>")

    html = re.sub(
        rf'<p><strong>({re.escape(doc_title)})</strong></p>',
        r'<h1 class="doc-title">\1</h1>',
        html, count=1
    )

    path.write_text(html, encoding="utf-8")
    print(f"✓ {path.name}")


def main():
    if len(sys.argv) < 3:
        print("Usage: style_html.py <output_dir> <org_label>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    org_label = sys.argv[2]

    for title in DOC_TITLES:
        html_path = output_dir / f"{title} ({org_label}).html"
        if html_path.exists():
            style_file(html_path, title)
        else:
            print(f"⚠ Не найден: {html_path.name}")


if __name__ == "__main__":
    main()
