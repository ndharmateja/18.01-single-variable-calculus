#!/usr/bin/env python3
"""
merge_by_number.py

Merge lecture note PDFs per number (001, 002, etc.) while:
1. Removing the last page of each PDF.
2. Ensuring combined pages per number are even.
3. Adding a filler page with '.' if needed.
"""

import io
import os
import re

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_dot_page(width_pts, height_pts):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width_pts, height_pts))
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(20, 20, ".")
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


# Folder containing PDFs
folder = "lecture-notes"

# Pattern: number + letter, e.g., 001a.pdf
pattern = re.compile(r"(\d+)([a-z])\.pdf", re.IGNORECASE)

# Collect files by number
files_by_number = {}
for f in os.listdir(folder):
    m = pattern.match(f)
    if m:
        number, letter = m.groups()
        files_by_number.setdefault(number, []).append(os.path.join(folder, f))

out = PdfWriter()

total_extra_pages_added = 0
for number in sorted(files_by_number.keys(), key=int):
    pdfs = sorted(files_by_number[number])  # sort alphabetically by letter
    print(f"Processing number {number}")
    page_width = page_height = None
    start_page_count = len(out.pages)

    for pdf_path in pdfs:
        reader = PdfReader(pdf_path)
        if len(reader.pages) == 0:
            continue
        # get page size from first page
        if page_width is None:
            p0 = reader.pages[0]
            page_width = float(p0.mediabox.width)
            page_height = float(p0.mediabox.height)
        # add all pages except last
        for i in range(max(0, len(reader.pages) - 1)):
            out.add_page(reader.pages[i])

    # ensure even page count per number
    pages_added = len(out.pages) - start_page_count
    if pages_added % 2 != 0:
        print(f"   Adding filler page to make even pages for {number}")
        total_extra_pages_added += 1
        if page_width is None or page_height is None:
            page_width, page_height = A4
        out.add_page(create_dot_page(page_width, page_height))

# Save final merged PDF
out_path = "lecture-notes-merged.pdf"
with open(out_path, "wb") as fo:
    out.write(fo)

print(f"Merged PDF saved as {out_path}")
print(f"Total extra pages added: {total_extra_pages_added}")
