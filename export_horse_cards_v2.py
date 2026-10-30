#!/usr/bin/env python3
"""
Horse Stars PDF -> WebP exporter v2

Strategy:
- Regular PDF: map pages by page order to all horses with rarity == "normal",
  sorted by card number.
- Specials PDF: detect card ID/name from page text and map to horses.json.
- Render PDF TrimBox to sRGB WebP.
- Name files like hs001-ezora.webp.
- Never silently invent a match for special cards.

Requirements:
    python3 -m pip install pymupdf pillow

Example:
    python3 export_horse_cards_v2.py \
      --json src/data/horses.json \
      --regular-pdf "public/images/cards/Cards-HS-regular print.pdf" \
      --special-pdf "public/images/cards/Card-HS-Specials.pdf" \
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
    import fitz  # PyMuPDF
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
        raise ValueError("horses.json must be a list or contain a 'horses' list.")

    # Sort once by card number.
    horses = sorted(horses, key=lambda h: int(h.get("number", 999999)))

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


def is_normal(horse) -> bool:
    return str(horse.get("rarity", "")).strip().lower() in {"normal", "standard"}


def detect_special_horse(page_text: str, by_id, by_name):
    # Preferred: card ID such as HS009, HS051, etc.
    normalized = page_text.upper()
    candidates = re.findall(r"\b([A-Z]{2})\s*[- ]?\s*(\d{3})\b", normalized)
    for prefix, digits in candidates:
        card_id = f"{prefix}{digits}"
        if card_id in by_id:
            return by_id[card_id], f"id:{card_id}"

    # Fallback: exactly one known horse name occurs in the page text.
    text_cf = page_text.casefold()
    matches = []
    for name_cf, horse in by_name.items():
        if re.search(rf"(?<!\w){re.escape(name_cf)}(?!\w)", text_cf):
            matches.append(horse)

    unique = {str(h.get("id")): h for h in matches if h.get("id")}
    if len(unique) == 1:
        horse = next(iter(unique.values()))
        return horse, f"name:{horse.get('name')}"

    return None, None


def best_clip(page):
    """
    Prefer TrimBox so printer bleed/crop marks do not become part of web art.
    """
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

    pix = page.get_pixmap(
        matrix=matrix,
        colorspace=fitz.csRGB,
        alpha=False,
        clip=clip,
    )

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=quality, method=6)


def output_filename(horse):
    hid = str(horse["id"]).lower()
    slug = horse.get("slug") or slugify(str(horse.get("name", "")))
    return f"{hid}-{slug}.webp"


def export_regular(pdf_path: Path, normal_horses, out_dir: Path, height: int, quality: int, overwrite: bool, report):
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    horse_count = len(normal_horses)

    report["regular"] = {
        "pdf": pdf_path.name,
        "pages": page_count,
        "expected_normal_horses": horse_count,
        "page_count_matches": page_count == horse_count,
    }

    print(f"\nREGULAR: {pdf_path.name}")
    print(f"PDF pages: {page_count}")
    print(f"Normal horses in JSON: {horse_count}")

    if page_count != horse_count:
        print("WARNING: Regular PDF page count does not equal number of normal horses.")
        print("The script will only map the overlapping range and report the mismatch.")

    count = min(page_count, horse_count)

    for idx in range(count):
        page = doc[idx]
        horse = normal_horses[idx]
        out_path = out_dir / output_filename(horse)

        if out_path.exists() and not overwrite:
            report["skipped_existing"].append({
                "type": "regular",
                "page": idx + 1,
                "id": horse.get("id"),
                "name": horse.get("name"),
                "file": str(out_path),
            })
            continue

        render_page_to_webp(page, out_path, height, quality)
        report["exported"].append({
            "type": "regular",
            "page": idx + 1,
            "id": horse.get("id"),
            "name": horse.get("name"),
            "file": str(out_path),
            "matched_by": "page_order",
        })
        print(f"  + page {idx+1:03d} -> {horse.get('id')} {horse.get('name')}")

    # Extra PDF pages beyond normal horse count go to unmatched.
    if page_count > horse_count:
        for idx in range(horse_count, page_count):
            page = doc[idx]
            fallback = out_dir / "_unmatched" / f"_unmatched-regular-page-{idx+1:03d}.webp"
            render_page_to_webp(page, fallback, height, quality)
            report["unmatched"].append({
                "type": "regular_extra_page",
                "page": idx + 1,
                "rendered_as": str(fallback),
            })

    # If JSON contains more normal horses than pages, report them.
    if horse_count > page_count:
        for horse in normal_horses[page_count:]:
            report["missing_regular_pages"].append({
                "id": horse.get("id"),
                "name": horse.get("name"),
            })

    doc.close()


def export_specials(pdf_path: Path, by_id, by_name, out_dir: Path, height: int, quality: int, overwrite: bool, report):
    doc = fitz.open(pdf_path)

    print(f"\nSPECIALS: {pdf_path.name}")
    print(f"PDF pages: {len(doc)}")

    seen_special_ids = set()

    for idx, page in enumerate(doc):
        page_no = idx + 1
        text = page.get_text("text") or ""
        horse, match_method = detect_special_horse(text, by_id, by_name)

        if not horse:
            fallback = out_dir / "_unmatched" / f"_unmatched-special-page-{page_no:03d}.webp"
            render_page_to_webp(page, fallback, height, quality)
            report["unmatched"].append({
                "type": "special",
                "page": page_no,
                "rendered_as": str(fallback),
                "text_preview": " ".join(text.split())[:250],
            })
            print(f"  ? page {page_no:03d} unmatched")
            continue

        horse_id = str(horse.get("id", "")).upper()

        # Do not accept a normal horse from the specials PDF silently.
        if is_normal(horse):
            fallback = out_dir / "_unmatched" / f"_unmatched-special-page-{page_no:03d}.webp"
            render_page_to_webp(page, fallback, height, quality)
            report["unmatched"].append({
                "type": "special_matched_normal_record",
                "page": page_no,
                "detected_id": horse_id,
                "detected_name": horse.get("name"),
                "rendered_as": str(fallback),
            })
            print(f"  ! page {page_no:03d} matched NORMAL horse {horse_id}; sent to unmatched")
            continue

        if horse_id in seen_special_ids:
            report["duplicates"].append({
                "type": "special",
                "page": page_no,
                "id": horse_id,
                "name": horse.get("name"),
            })
            print(f"  ! page {page_no:03d} duplicate special {horse_id}")
            continue

        seen_special_ids.add(horse_id)
        out_path = out_dir / output_filename(horse)

        if out_path.exists() and not overwrite:
            report["skipped_existing"].append({
                "type": "special",
                "page": page_no,
                "id": horse_id,
                "name": horse.get("name"),
                "file": str(out_path),
            })
            continue

        render_page_to_webp(page, out_path, height, quality)
        report["exported"].append({
            "type": "special",
            "page": page_no,
            "id": horse_id,
            "name": horse.get("name"),
            "file": str(out_path),
            "matched_by": match_method,
        })
        print(f"  + page {page_no:03d} -> {horse_id} {horse.get('name')} ({match_method})")

    doc.close()


def main():
    parser = argparse.ArgumentParser(description="Horse Stars PDF -> WebP exporter v2")
    parser.add_argument("--json", required=True)
    parser.add_argument("--regular-pdf", required=True)
    parser.add_argument("--special-pdf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--height", type=int, default=1200)
    parser.add_argument("--quality", type=int, default=86)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    json_path = Path(args.json).expanduser().resolve()
    regular_pdf = Path(args.regular_pdf).expanduser().resolve()
    special_pdf = Path(args.special_pdf).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    horses, by_id, by_name = load_horses(json_path)
    normal_horses = [h for h in horses if is_normal(h)]
    special_horses = [h for h in horses if not is_normal(h)]

    report = {
        "dataset": {
            "total_horses": len(horses),
            "normal_horses": len(normal_horses),
            "special_horses": len(special_horses),
        },
        "exported": [],
        "skipped_existing": [],
        "unmatched": [],
        "duplicates": [],
        "missing_regular_pages": [],
    }

    if not regular_pdf.exists():
        sys.exit(f"Regular PDF not found: {regular_pdf}")
    if not special_pdf.exists():
        sys.exit(f"Special PDF not found: {special_pdf}")

    export_regular(
        regular_pdf, normal_horses, out_dir,
        args.height, args.quality, args.overwrite, report
    )

    export_specials(
        special_pdf, by_id, by_name, out_dir,
        args.height, args.quality, args.overwrite, report
    )

    # Final presence check for all 102 JSON records.
    missing_after_export = []
    present = []

    for horse in horses:
        expected = out_dir / output_filename(horse)
        if expected.exists():
            present.append({
                "id": horse.get("id"),
                "name": horse.get("name"),
                "file": str(expected),
            })
        else:
            missing_after_export.append({
                "id": horse.get("id"),
                "name": horse.get("name"),
                "rarity": horse.get("rarity"),
                "expected_file": str(expected),
            })

    report["present_after_export"] = present
    report["missing_after_export"] = missing_after_export

    report_path = out_dir / "horse-card-export-report-v2.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n=== SUMMARY ===")
    print(f"Dataset horses: {len(horses)}")
    print(f"Normal horses: {len(normal_horses)}")
    print(f"Special horses: {len(special_horses)}")
    print(f"Newly exported: {len(report['exported'])}")
    print(f"Already existed / skipped: {len(report['skipped_existing'])}")
    print(f"Unmatched pages: {len(report['unmatched'])}")
    print(f"Duplicate special detections: {len(report['duplicates'])}")
    print(f"Card files present: {len(present)} / {len(horses)}")
    print(f"Still missing: {len(missing_after_export)}")
    print(f"Report: {report_path}")

    if missing_after_export:
        print("\nStill missing:")
        for item in missing_after_export:
            print(f"  - {item['id']} {item['name']} ({item.get('rarity')})")


if __name__ == "__main__":
    main()
