#!/usr/bin/env python3
"""Render book PDFs into stamped WebP page images.

Usage: python3 scripts/render_pages.py --books data/books.json --pdf-dir <dir> --out site
PDF files are expected at <pdf-dir>/<slug>-<volid>.pdf (downloaded from the
public URLs in books.json by the workflow, or placed there locally).
Output: <out>/img/<slug>/<volid>/p0001.webp ...
Each page image gets the site header 「冯氏族谱 · fengshizupu.com」 stamped at
the top-left: deep red on light pages, cream white on dark pages (auto).
Source-library watermarks inside the scans are kept as-is.
"""
import argparse, io, json, os, sys
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

HEADER = "冯氏族谱 · fengshizupu.com"
RED = (116, 47, 50)
CREAM = (255, 244, 223)

FONT_CANDIDATES = [
    os.environ.get("STAMP_FONT", ""),
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Bold.ttc",
    os.path.expanduser("~/workspace/fengshizupu-work/book/fonts/NotoSerifSC-700.ttf"),
]


def load_font(size):
    for path in FONT_CANDIDATES:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def page_image(doc, page):
    """Extract the page's embedded scan image; fall back to rendering."""
    imgs = page.get_images(full=True)
    if imgs:
        xref = imgs[0][0]
        d = doc.extract_image(xref)
        return Image.open(io.BytesIO(d["image"])).convert("RGB")
    pix = page.get_pixmap(dpi=150)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def stamp(img):
    w, h = img.size
    # luminance of the top strip where the header will sit
    strip = img.crop((0, 0, max(1, int(w * 0.62)), max(1, int(h * 0.055)))).convert("L")
    px = list(strip.getdata())
    lum = sum(px) / max(1, len(px))
    color = CREAM if lum < 110 else RED
    size = max(18, round(w * 0.026))
    font = load_font(size)
    draw = ImageDraw.Draw(img)
    draw.text((round(w * 0.024), round(h * 0.011)), HEADER, font=font, fill=color)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", required=True)
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.load(open(args.books, encoding="utf-8"))
    total_pages, total_bytes = 0, 0
    for book in data["books"]:
        for vol in book["volumes"]:
            pdf = os.path.join(args.pdf_dir, f'{book["slug"]}-{vol["id"]}.pdf')
            if not os.path.exists(pdf):
                print(f'MISSING PDF: {pdf}', file=sys.stderr)
                return 1
            outdir = os.path.join(args.out, "img", book["slug"], vol["id"])
            os.makedirs(outdir, exist_ok=True)
            doc = fitz.open(pdf)
            if doc.page_count != vol["pages"]:
                print(f'WARN {book["slug"]}/{vol["id"]}: books.json says {vol["pages"]} pages, PDF has {doc.page_count}')
            for i, page in enumerate(doc, start=1):
                img = stamp(page_image(doc, page))
                target = os.path.join(outdir, f"p{i:04d}.webp")
                img.save(target, "WEBP", quality=80)
                total_bytes += os.path.getsize(target)
                total_pages += 1
            print(f'{book["slug"]}/{vol["id"]}: {doc.page_count} pages rendered')
            doc.close()
    print(f"TOTAL: {total_pages} pages, {total_bytes/1048576:.1f} MB of WebP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
