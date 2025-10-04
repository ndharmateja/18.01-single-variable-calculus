#!/usr/bin/env python3
"""
merge_examples_problems.py

Merges all PDFs from examples/problems/ into one PDF with:
- Last page of each file removed
- Even total pages per file (adds a filler page with a small dot)
"""

import io
import os
import re

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

input_folder = "examples/problems"
output_file = "example-problems-merged.pdf"


# --- Create filler page with a small dot ---
def create_dot_page(width_pts, height_pts):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width_pts, height_pts))
    c.setFont("Helvetica", 8)
    c.drawString(20, 20, ".")
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


# --- Collect PDF files ---
pattern = re.compile(r"ex(\d{3})prb\.pdf", re.IGNORECASE)
files = []
for f in os.listdir(input_folder):
    if pattern.match(f):
        files.append(f)

if not files:
    raise SystemExit("No matching PDFs found in examples/problems/")

# --- Sort numerically ---
files.sort(key=lambda x: int(re.search(r"ex(\d{3})", x).group(1)))

# --- Merge ---
out = PdfWriter()
for f in files:
    path = os.path.join(input_folder, f)
    print(f"Processing {f} ...")
    reader = PdfReader(path)
    n_pages = len(reader.pages)
    if n_pages <= 1:
        continue  # skip single-page files

    first_page = reader.pages[0]
    w, h = float(first_page.mediabox.width), float(first_page.mediabox.height)

    # Add all pages except last
    for i in range(n_pages - 1):
        out.add_page(reader.pages[i])

    # Ensure even count
    if (n_pages - 1) % 2 != 0:
        filler_page = create_dot_page(w, h)
        out.add_page(filler_page)
        print(f"  ➕ Added filler page for {f}")

# --- Save output ---
with open(output_file, "wb") as fout:
    out.write(fout)

print(f"\n✅ Done! Saved merged PDF as {output_file}")
