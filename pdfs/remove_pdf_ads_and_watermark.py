from __future__ import annotations

from pathlib import Path
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install pymupdf")
    sys.exit(1)


INPUT_FOLDERS = (Path("pdfs/input"), Path("pdfs/input_pdf"))
OUTPUT_FOLDER = Path("pdfs/output_pdf_remove_pdf_ads_and_watermark")

# Put every exact visible text string here that you want to remove.
TEXT_STRINGS_TO_REMOVE = [
    "CLICK HERE - JOIN @YCTBOOKS",
    "@Yctbooks",
    "FREE PDF Notes Click NOW",
    "CLICK HERE — UPSC /UPPCS /BPSC  STUDY MATERIAL",
    "Made with Xodo PDF Reader and Editor",
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
    "https://t.me/yctbooks",
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


def find_input_folder() -> Path:
    for folder in INPUT_FOLDERS:
        if folder.is_dir():
            return folder
    return INPUT_FOLDERS[0]


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


def disable_watermark_patterns(doc: fitz.Document, watermark_texts: list[str]) -> int:
    """Disable reusable Pattern/Form streams containing a watermark string.

    The sample PDF places @Yctbooks in a tiling Pattern over the page image.
    Removing that stream preserves the raster page underneath, including text
    that the diagonal watermark crosses visually.
    """
    needles = [text.encode("latin1", errors="ignore").lower()
               for text in watermark_texts if text.strip()]
    disabled = 0

    for xref in range(1, doc.xref_length()):
        try:
            stream = doc.xref_stream(xref)
            object_text = doc.xref_object(xref, compressed=False)
        except Exception:
            continue

        if not stream or not any(needle in stream.lower() for needle in needles):
            continue
        object_lower = object_text.lower()
        if "/type /pattern" not in object_lower and "/subtype /form" not in object_lower:
            continue

        doc.update_stream(xref, b"q\nQ\n")
        disabled += 1

    return disabled


def disable_private_watermark_streams(doc: fitz.Document) -> int:
    """Disable PDFTron/Xodo watermark content streams without touching pages."""
    disabled = 0
    for xref in range(1, doc.xref_length()):
        try:
            object_text = doc.xref_object(xref, compressed=False)
            stream = doc.xref_stream(xref)
        except Exception:
            continue

        object_lower = object_text.lower()
        if not stream or "/pdftron" not in object_lower or "/private /watermark" not in object_lower:
            continue

        doc.update_stream(xref, b"q\nQ\n")
        disabled += 1
    return disabled


def remove_positioned_ad_text_streams(doc: fitz.Document) -> int:
    """Remove the encoded bottom ad while preserving nearby page numbers.

    The bottom ad is a separate BT/ET block at x=56.22, y=40 in the PDF
    content stream. Removing only that block avoids painting over page numbers.
    """
    removed = 0
    marker = b"BT\n1 0 0 1 56.22 40 Tm\n"

    for xref in range(1, doc.xref_length()):
        try:
            stream = doc.xref_stream(xref)
        except Exception:
            continue
        if not stream or marker not in stream:
            continue

        start = stream.find(marker)
        end = stream.find(b"ET\n", start)
        if end < 0:
            continue
        end += len(b"ET\n")
        doc.update_stream(xref, stream[:start] + stream[end:])
        removed += 1

    return removed


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
    pattern_matches = disable_watermark_patterns(doc, ["@Yctbooks", "VikasNCERT"])
    private_watermark_matches = disable_private_watermark_streams(doc)
    positioned_ad_matches = remove_positioned_ad_text_streams(doc)

    for page in doc:
        total_matches += delete_matching_links(page, target_uris)
        total_matches += mask_remaining_text_matches(page, target_texts)

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True)
    page_count = doc.page_count
    doc.close()
    return (
        page_count,
        total_matches + pattern_matches + private_watermark_matches + positioned_ad_matches,
    )


def main() -> None:
    input_folder = find_input_folder()
    pdf_files = iter_pdf_files(input_folder)
    if not pdf_files:
        print(f"No PDF files found in: {input_folder}")
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
