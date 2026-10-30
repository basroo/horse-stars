#!/usr/bin/env python3
"""
Horse Stars PDF -> WebP exporter

Requirements:
    python3 -m pip install pymupdf pillow

Example:
    python3 export_horse_cards.py \
      --json src/data/horses.json \
      --pdf "public/images/cards/Cards-HS-regular print.pdf" \
      --pdf "public/images/cards/Card-HS-Specials.pdf" \
      --out public/images/cards \
      --height 1200 \
      --quality 86
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("Missing PyMuPDF. Install with: python3 -m pip install pymupdf pillow")

try:
    from PIL import Image
except ImportError:
    sys.exit("Missing Pillow. Install with: python3 -m pip install pymupdf pillow")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def load_horses(json_path: Path):
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        horses = data
    elif isinstance(data, dict) and isinstance(data.get("horses"), list):
        horses = data["horses"]
    else:
        raise ValueError("horses.json must be a list, or an object containing a 'horses' list.")

    by_id = {}
    by_name = {}
    for horse in horses:
        hid = str(horse.get("id", "")).upper().replace(" ", "")
        name = str(horse.get("name", "")).strip()
        if hid:
            by_id[hid] = horse
        if name:
            by_name[name.casefold()] = horse
    return horses, by_id, by_name


def detect_horse(page_text: str, by_id, by_name):
    normalized = page_text.upper()
    candidates = re.findall(r"\b([A-Z]{2})\s*[- ]?\s*(\d{3})\b", normalized)
    for prefix, digits in candidates:
        card_id = f"{prefix}{digits}"
        if card_id in by_id:
            return by_id[card_id], f"id:{card_id}"

    text_cf = page_text.casefold()
    matches = []
    for name_cf, horse in by_name.items():
        if re.search(rf"(?<!\w){re.escape(name_cf)}(?!\w)", text_cf):
            matches.append(horse)

    unique = {h["id"]: h for h in matches if h.get("id")}
    if len(unique) == 1:
        horse = next(iter(unique.values()))
        return horse, f"name:{horse.get('name')}"
    return None, None


def best_clip(page):
    for attr in ("trimbox", "cropbox"):
        try:
            rect = getattr(page, attr)
            if rect and rect.width > 0 and rect.height > 0:
                return rect
        except Exception:
            pass
    return page.rect


def render_page_to_webp(page, out_path: Path, target_height: int, quality: int):
    clip = best_clip(page)
    scale = target_height / clip.height
    matrix = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False, clip=clip)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=quality, method=6)


def output_filename(horse):
    hid = str(horse["id"]).lower()
    slug = horse.get("slug") or slugify(str(horse.get("name", "")))
    return f"{hid}-{slug}.webp"


def main():
    parser = argparse.ArgumentParser(description="Export Horse Stars card PDFs to named WebP files.")
    parser.add_argument("--json", required=True, help="Path to horses.json")
    parser.add_argument("--pdf", action="append", required=True,
                        help="PDF to process. Repeat --pdf for multiple PDFs.")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--height", type=int, default=1200, help="Target height in pixels")
    parser.add_argument("--quality", type=int, default=86, help="WebP quality 1-100")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing WebP files")
    args = parser.parse_args()

    json_path = Path(args.json).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    horses, by_id, by_name = load_horses(json_path)

    report = {"exported": [], "unmatched": [], "duplicates": [], "skipped_existing": []}
    seen_ids = set()

    for pdf_arg in args.pdf:
        pdf_path = Path(pdf_arg).expanduser().resolve()
        if not pdf_path.exists():
            report["unmatched"].append({"pdf": str(pdf_path), "reason": "file_not_found"})
            continue

        doc = fitz.open(pdf_path)
        print(f"Processing {pdf_path.name}: {len(doc)} pages")

        for page_index, page in enumerate(doc):
            page_no = page_index + 1
            text = page.get_text("text") or ""
            horse, match_method = detect_horse(text, by_id, by_name)

            if not horse:
                fallback_name = f"_unmatched-{slugify(pdf_path.stem)}-page-{page_no:03d}.webp"
                fallback_path = out_dir / "_unmatched" / fallback_name
                render_page_to_webp(page, fallback_path, args.height, args.quality)
                report["unmatched"].append({
                    "pdf": pdf_path.name,
                    "page": page_no,
                    "rendered_as": str(fallback_path),
                    "text_preview": " ".join(text.split())[:250],
                })
                continue

            horse_id = str(horse["id"]).upper()
            if horse_id in seen_ids:
                report["duplicates"].append({
                    "pdf": pdf_path.name, "page": page_no,
                    "id": horse_id, "name": horse.get("name"),
                })
                continue

            seen_ids.add(horse_id)
            out_path = out_dir / output_filename(horse)

            if out_path.exists() and not args.overwrite:
                report["skipped_existing"].append({"id": horse_id, "file": str(out_path)})
                continue

            render_page_to_webp(page, out_path, args.height, args.quality)
            report["exported"].append({
                "pdf": pdf_path.name,
                "page": page_no,
                "id": horse_id,
                "name": horse.get("name"),
                "file": str(out_path),
                "matched_by": match_method,
            })

        doc.close()

    missing = []
    for horse in horses:
        expected = out_dir / output_filename(horse)
        if not expected.exists():
            missing.append({
                "id": horse.get("id"),
                "name": horse.get("name"),
                "expected_file": str(expected),
            })
    report["missing_after_export"] = missing

    report_path = out_dir / "horse-card-export-report.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Exported: {len(report['exported'])}")
    print(f"Unmatched pages: {len(report['unmatched'])}")
    print(f"Duplicates: {len(report['duplicates'])}")
    print(f"Missing after export: {len(report['missing_after_export'])}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
