from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install pymupdf")
    sys.exit(1)


KEYWORDS = [
    "telegram",
    "t.me",
    "join telegram",
    "telegram group",
    "telegram channel",
    "CLICK HERE"
    "https://t.me/youthpublicationbook"
]


def add_band_redactions(page: fitz.Page, top_ratio: float, bottom_ratio: float) -> None:
    rect = page.rect
    top_height = rect.height * top_ratio
    bottom_height = rect.height * bottom_ratio

    if top_height > 0:
        page.add_redact_annot(
            fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + top_height),
            fill=(1, 1, 1),
        )

    if bottom_height > 0:
        page.add_redact_annot(
            fitz.Rect(rect.x0, rect.y1 - bottom_height, rect.x1, rect.y1),
            fill=(1, 1, 1),
        )


def add_keyword_redactions(page: fitz.Page, keywords: list[str]) -> int:
    matches = 0
    for keyword in keywords:
        for rect in page.search_for(keyword, quads=False):
            page.add_redact_annot(rect, fill=(1, 1, 1))
            matches += 1
    return matches


def clean_pdf(
    input_pdf: Path,
    output_pdf: Path,
    top_ratio: float,
    bottom_ratio: float,
    remove_keywords: bool,
) -> tuple[int, int]:
    doc = fitz.open(input_pdf)
    keyword_hits = 0

    for page in doc:
        add_band_redactions(page, top_ratio, bottom_ratio)
        if remove_keywords:
            keyword_hits += add_keyword_redactions(page, KEYWORDS)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True)
    page_count = doc.page_count
    doc.close()
    return page_count, keyword_hits


def iter_pdf_files(target: Path) -> list[Path]:
    if target.is_file() and target.suffix.lower() == ".pdf":
        return [target]
    if target.is_dir():
        return sorted(path for path in target.iterdir() if path.suffix.lower() == ".pdf")
    return []


def build_output_path(source: Path, base_target: Path) -> Path:
    if base_target.suffix.lower() == ".pdf":
        return base_target
    return base_target / f"{source.stem}_cleaned.pdf"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove Telegram advertisement areas from PDF pages."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        default="pdfs/input_pdf1",
        help="PDF file or folder containing PDFs. Default: pdfs/input_pdf1",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output PDF or output folder. Default is auto-created next to input.",
    )
    parser.add_argument(
        "--top-ratio",
        type=float,
        default=0.03,
        help="Top area to erase on every page. Default: 0.03",
    )
    parser.add_argument(
        "--bottom-ratio",
        type=float,
        default=0.03,
        help="Bottom area to erase on every page. Default: 0.03",
    )
    parser.add_argument(
        "--no-keywords",
        action="store_true",
        help="Do not remove Telegram text matches outside the top and bottom bands.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_path)

    if not 0 <= args.top_ratio < 1 or not 0 <= args.bottom_ratio < 1:
        print("top-ratio and bottom-ratio must be between 0 and 1.")
        sys.exit(1)

    pdf_files = iter_pdf_files(input_path)
    if not pdf_files:
        print(f"No PDF files found in: {input_path}")
        sys.exit(1)

    if args.output:
        output_target = Path(args.output)
    elif input_path.is_file():
        output_target = input_path.with_name(f"{input_path.stem}_cleaned.pdf")
    else:
        output_target = input_path.parent / f"{input_path.name}_cleaned_out"

    processed = 0
    for pdf_file in pdf_files:
        output_pdf = build_output_path(pdf_file, output_target)
        try:
            pages, keyword_hits = clean_pdf(
                pdf_file,
                output_pdf,
                args.top_ratio,
                args.bottom_ratio,
                remove_keywords=not args.no_keywords,
            )
            processed += 1
            print(
                f"Cleaned: {pdf_file.name} | pages: {pages} | keyword matches removed: {keyword_hits}"
            )
            print(f"Saved to: {output_pdf}")
        except Exception as exc:
            print(f"Failed: {pdf_file.name} ({exc})")

    print(f"Finished. Total PDFs processed: {processed}")


if __name__ == "__main__":
    main()
