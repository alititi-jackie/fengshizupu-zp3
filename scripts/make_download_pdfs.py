#!/usr/bin/env python3
"""Build downloadable PDFs with the site header stamped on every page.

The pristine source PDFs stay untouched (archive + build inputs). This script
produces separate "-dl" PDFs: each page image is stamped with
「冯氏族谱 · fengshizupu.com」at the top-left (same position/colour logic as
scripts/render_pages.py) and reassembled into a PDF at the source page size.

Usage:
  python3 scripts/make_download_pdfs.py --books data/books.json \
      --pdf-dir <dir with <slug>-<volid>.pdf> --out <dir>
Output: <out>/<slug>-<volid>-dl.pdf  (plus a sizes report on stdout)
"""
import argparse
import io
import json
import os
import sys

import fitz  # PyMuPDF
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_pages import stamp  # 页眉样式以 render_pages 为唯一出处，两边不要各改各的


def page_image(doc, page):
    # 下载版取每页最大的内嵌图、无图时 200dpi 渲染（网页版 render_pages 取首图/150dpi，印刷版要更清）
    imgs = page.get_images(full=True)
    if imgs:
        xref = max(imgs, key=lambda im: im[2] * im[3])[0]
        try:
            d = doc.extract_image(xref)
            return Image.open(io.BytesIO(d["image"])).convert("RGB")
        except Exception:
            pass
    pix = page.get_pixmap(dpi=200)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def build(pdf_path, out_path):
    src = fitz.open(pdf_path)
    out = fitz.open()
    for page in src:
        img = stamp(page_image(src, page))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=88)
        new = out.new_page(width=page.rect.width, height=page.rect.height)
        new.insert_image(new.rect, stream=buf.getvalue())
    out.save(out_path, deflate=True, garbage=3)
    n = len(src)
    src.close()
    out.close()
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", required=True)
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.load(open(args.books, encoding="utf-8"))
    os.makedirs(args.out, exist_ok=True)
    for book in data["books"]:
        for vol in book["volumes"]:
            src = os.path.join(args.pdf_dir, f'{book["slug"]}-{vol["id"]}.pdf')
            dst = os.path.join(args.out, f'{book["slug"]}-{vol["id"]}-dl.pdf')
            n = build(src, dst)
            size = os.path.getsize(dst)
            print(f'{vol["id"]}: {n} pages, {size} bytes ({size/1048576:.1f} MB) -> {dst}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
