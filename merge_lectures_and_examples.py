#!/usr/bin/env python3
"""
merge_lectures_and_examples.py

==============================================================
📘 PURPOSE
--------------------------------------------------------------
This script merges lecture PDFs and example problem PDFs
according to your constraints:

1. Input folders:
   - lecture-notes/ (files like 001a.pdf, 001b.pdf, etc)
   - examples/problems/ (files like ex001prb.pdf, ex002prb.pdf, etc)

2. For each lecture number (001, 002, ...):
   - Merge all matching lecture files (001a.pdf, 001b.pdf, ...)
   - Then merge the corresponding example PDF (if exists)
   - Remove the **last page** of each individual file
   - Ensure total pages per lecture block is **even**
   - Add a **filler page with a dot** if needed (prevents blank-page skip when printing)

3. Output:
   - Single merged file: merged_output.pdf

==============================================================
"""

import io
import os
import re

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# -------------------------------------------------------------
# Helper: create a dot filler page
# -------------------------------------------------------------
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


# -------------------------------------------------------------
# Collect files
# -------------------------------------------------------------
def collect_lecture_files(folder):
    """
    Collects lecture files like 001a.pdf, 001b.pdf, etc.
    Returns dict: { "001": ["001a.pdf", "001b.pdf", ...], ... }
    """
    mapping = {}
    pattern = re.compile(r"(\d{3})([a-z])\.pdf", re.IGNORECASE)
    for f in sorted(os.listdir(folder)):
        m = pattern.match(f)
        if m:
            num = m.group(1)
            mapping.setdefault(num, []).append(os.path.join(folder, f))
    return mapping


def collect_example_files(folder):
    """
    Collects example problem files like ex001prb.pdf
    Returns dict: { "001": "ex001prb.pdf", ... }
    """
    mapping = {}
    pattern = re.compile(r"ex(\d{3})prb\.pdf", re.IGNORECASE)
    for f in os.listdir(folder):
        m = pattern.match(f)
        if m:
            num = m.group(1)
            mapping[num] = os.path.join(folder, f)
    return mapping


# -------------------------------------------------------------
# STEP 1: Gather files
# -------------------------------------------------------------
lecture_folder = "lecture-notes"
example_folder = "examples/problems"

lectures = collect_lecture_files(lecture_folder)
examples = collect_example_files(example_folder)

print(f"📚 Found {len(lectures)} lecture groups and {len(examples)} example PDFs.\n")

out = PdfWriter()

# -------------------------------------------------------------
# STEP 2: Merge PDFs by lecture number
# -------------------------------------------------------------
for num in sorted(lectures.keys()):
    print(f"\n🔹 Processing Lecture {num}")

    page_width = None
    page_height = None
    start_page_count = len(out.pages)

    # ---- Merge lecture files ----
    for path in sorted(lectures[num]):
        print(f"   📘 Adding {os.path.basename(path)} (excluding last page)")
        r = PdfReader(path)
        if len(r.pages) == 0:
            continue
        if page_width is None:
            p0 = r.pages[0]
            page_width = float(p0.mediabox.width)
            page_height = float(p0.mediabox.height)
        for i in range(max(0, len(r.pages) - 1)):
            out.add_page(r.pages[i])

    # ---- Merge example if exists ----
    if num in examples:
        ex_path = examples[num]
        print(f"   🧩 Adding Example {os.path.basename(ex_path)} (excluding last page)")
        r = PdfReader(ex_path)
        if len(r.pages) > 0:
            if page_width is None:
                p0 = r.pages[0]
                page_width = float(p0.mediabox.width)
                page_height = float(p0.mediabox.height)
            for i in range(max(0, len(r.pages) - 1)):
                out.add_page(r.pages[i])
    else:
        print("   ⚠️ No example found for this lecture.")

    # ---- Ensure even page count ----
    pages_added = len(out.pages) - start_page_count
    if pages_added % 2 != 0:
        print("   ➕ Adding filler page with a '.' to make page count even.")
        if page_width is None or page_height is None:
            page_width, page_height = A4
        out.add_page(create_dot_page(page_width, page_height))

# -------------------------------------------------------------
# STEP 3: Save final output
# -------------------------------------------------------------
out_path = "lecture-notes-and-examples-merged.pdf"
with open(out_path, "wb") as fo:
    out.write(fo)

print(f"\n✅ Done! Final merged PDF saved as: {out_path}")
