from __future__ import annotations

from pathlib import Path
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install pymupdf")
    sys.exit(1)


INPUT_FOLDER = Path("pdfs/input_pdf")
OUTPUT_FOLDER = Path("pdfs/output_pdf_remove_telegram_ads")
TOP_RATIO = 0.00
BOTTOM_RATIO = 0.08
REMOVE_KEYWORDS = True

KEYWORDS = [
    "telegram",
    "t.me",
    "join telegram",
    "telegram group",
    "telegram channel",
    "CLICK HERE",
    "https://t.me/youthpublicationbook",
]


def iter_pdf_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.iterdir() if path.suffix.lower() == ".pdf")


def build_output_path(input_pdf: Path) -> Path:
    return OUTPUT_FOLDER / input_pdf.name


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

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True)
    page_count = doc.page_count
    doc.close()
    return page_count, keyword_hits


def main() -> None:
    pdf_files = iter_pdf_files(INPUT_FOLDER)
    if not pdf_files:
        print(f"No PDF files found in: {INPUT_FOLDER}")
        sys.exit(1)

    processed = 0
    for pdf_file in pdf_files:
        output_pdf = build_output_path(pdf_file)
        try:
            pages, keyword_hits = clean_pdf(
                pdf_file,
                output_pdf,
                TOP_RATIO,
                BOTTOM_RATIO,
                REMOVE_KEYWORDS,
            )
            processed += 1
            print(
                f"Removed telegram ads: {pdf_file.name} | pages: {pages} | keyword matches: {keyword_hits}"
            )
            print(f"Saved to: {output_pdf}")
        except Exception as exc:
            print(f"Failed: {pdf_file.name} ({exc})")

    print(f"Finished. Total PDFs processed: {processed}")


if __name__ == "__main__":
    main()
