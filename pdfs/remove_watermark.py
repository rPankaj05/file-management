from __future__ import annotations

from pathlib import Path
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install pymupdf")
    sys.exit(1)


INPUT_FOLDER = Path("pdfs/input_pdf")
OUTPUT_FOLDER = Path("pdfs/output_pdf_remove_watermark")
WATERMARK_TEXT = "@apna_pdf"


def iter_pdf_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.iterdir() if path.suffix.lower() == ".pdf")


def build_output_path(input_pdf: Path) -> Path:
    return OUTPUT_FOLDER / input_pdf.name


def find_watermark_pattern_xrefs(doc: fitz.Document, watermark_text: str) -> list[int]:
    hits: list[int] = []
    needle = watermark_text.encode("latin1", errors="ignore")

    for xref in range(1, doc.xref_length()):
        try:
            stream = doc.xref_stream(xref)
        except Exception:
            continue

        if not stream or needle not in stream:
            continue

        object_text = doc.xref_object(xref, compressed=False)
        if "/Type /Pattern" in object_text or "/Subtype /Form" in object_text:
            hits.append(xref)

    return hits


def disable_watermark_patterns(
    input_pdf: Path,
    output_pdf: Path,
    watermark_text: str,
) -> tuple[int, int]:
    doc = fitz.open(input_pdf)
    pattern_xrefs = find_watermark_pattern_xrefs(doc, watermark_text)

    for xref in pattern_xrefs:
        doc.update_stream(xref, b"q\nQ\n")

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True)
    page_count = doc.page_count
    doc.close()
    return page_count, len(pattern_xrefs)


def main() -> None:
    pdf_files = iter_pdf_files(INPUT_FOLDER)
    if not pdf_files:
        print(f"No PDF files found in: {INPUT_FOLDER}")
        sys.exit(1)

    processed = 0
    for pdf_file in pdf_files:
        output_pdf = build_output_path(pdf_file)
        try:
            pages, pattern_count = disable_watermark_patterns(
                pdf_file,
                output_pdf,
                WATERMARK_TEXT,
            )
            processed += 1
            print(
                f"Removed watermark: {pdf_file.name} | pages: {pages} | patterns: {pattern_count}"
            )
            print(f"Saved to: {output_pdf}")
        except Exception as exc:
            print(f"Failed: {pdf_file.name} ({exc})")

    print(f"Finished. Total PDFs processed: {processed}")


if __name__ == "__main__":
    main()
