from __future__ import annotations

from pathlib import Path
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install pymupdf")
    sys.exit(1)


INPUT_FOLDER = Path("pdfs/input_pdf")
OUTPUT_FOLDER = Path("pdfs/output_pdf_remove_pdf_ads_and_watermark")

# Put every exact visible text string here that you want to remove.
TEXT_STRINGS_TO_REMOVE = [
    "CLICK HERE - JOIN @APNAPDFS",
    "CLICK HERE — UPPCS NOTES 2026",
    "CLICK HERE — UPSC/UPPCS Notes",
    "Made with Xodo PDF Reader and Editor",
    "REXODAS",
    "Shubham Gupta Academy",
    "8989851047 – Shubham Gupta Academy"
]

# Put exact or partial link URIs here.
LINK_URIS_TO_REMOVE = [
    "https://t.me/pdfhub2021",
    "https://t.me/+e2JzB6EsQmo4YjU1",
    "https://play.google.com/store/apps/details?id=com.xodo.pdf.reader",
]

MASK_PADDING_X = 3
MASK_PADDING_Y = 4


def iter_pdf_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.iterdir() if path.suffix.lower() == ".pdf")


def build_output_path(input_pdf: Path) -> Path:
    return OUTPUT_FOLDER / input_pdf.name


def replace_exact_text_in_streams(doc: fitz.Document, target_texts: list[str]) -> int:
    matches = 0
    targets = [
        f"({text})".encode("latin1", errors="ignore")
        for text in target_texts
        if text.strip()
    ]

    for xref in range(1, doc.xref_length()):
        try:
            stream = doc.xref_stream(xref)
        except Exception:
            continue
        if not stream:
            continue

        updated = stream
        for target in targets:
            count_before = updated.count(target)
            if count_before:
                updated = updated.replace(target, b"()")
                matches += count_before

        if updated != stream:
            doc.update_stream(xref, updated)

    return matches


def delete_matching_links(page: fitz.Page, target_uris: list[str]) -> int:
    matches = 0
    normalized_uris = [uri.strip().lower() for uri in target_uris if uri.strip()]

    for link in page.get_links():
        uri = (link.get("uri") or "").strip().lower()
        if uri and any(target_uri in uri for target_uri in normalized_uris):
            try:
                page.delete_link(link)
            except Exception:
                pass
            matches += 1

    return matches


def mask_remaining_text_matches(page: fitz.Page, target_texts: list[str]) -> int:
    matches = 0

    for text in target_texts:
        if not text.strip():
            continue

        for rect in page.search_for(text):
            padded_rect = fitz.Rect(
                rect.x0 - MASK_PADDING_X,
                rect.y0 - MASK_PADDING_Y,
                rect.x1 + MASK_PADDING_X,
                rect.y1 + MASK_PADDING_Y,
            )
            page.draw_rect(
                padded_rect,
                color=(1, 1, 1),
                fill=(1, 1, 1),
                overlay=True,
            )
            matches += 1

    return matches


def remove_pdf_ads_and_watermark(
    input_pdf: Path,
    output_pdf: Path,
    target_texts: list[str],
    target_uris: list[str],
) -> tuple[int, int]:
    doc = fitz.open(input_pdf)
    total_matches = replace_exact_text_in_streams(doc, target_texts)

    for page in doc:
        total_matches += delete_matching_links(page, target_uris)
        total_matches += mask_remaining_text_matches(page, target_texts)

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True)
    page_count = doc.page_count
    doc.close()
    return page_count, total_matches


def main() -> None:
    pdf_files = iter_pdf_files(INPUT_FOLDER)
    if not pdf_files:
        print(f"No PDF files found in: {INPUT_FOLDER}")
        sys.exit(1)

    processed = 0
    for pdf_file in pdf_files:
        output_pdf = build_output_path(pdf_file)
        try:
            pages, total_matches = remove_pdf_ads_and_watermark(
                pdf_file,
                output_pdf,
                TEXT_STRINGS_TO_REMOVE,
                LINK_URIS_TO_REMOVE,
            )
            processed += 1
            print(
                f"Removed ads/watermark: {pdf_file.name} | pages: {pages} | matches: {total_matches}"
            )
            print(f"Saved to: {output_pdf}")
        except Exception as exc:
            print(f"Failed: {pdf_file.name} ({exc})")

    print(f"Finished. Total PDFs processed: {processed}")


if __name__ == "__main__":
    main()
