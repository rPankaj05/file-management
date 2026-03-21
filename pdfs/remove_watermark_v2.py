from __future__ import annotations

from pathlib import Path
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install pymupdf")
    sys.exit(1)


INPUT_FOLDER = Path("pdfs/input_pdf")
OUTPUT_FOLDER = Path("pdfs/output_pdf_remove_watermark_v2")
WATERMARK_TEXTS = [
    "@freepdfhall",
    "@apna_pdf",
    "@apna_yct",
    "CLICK HERE",
    "CLICK"
]


def iter_pdf_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.iterdir() if path.suffix.lower() == ".pdf")


def build_output_path(input_pdf: Path) -> Path:
    return OUTPUT_FOLDER / input_pdf.name


def replace_watermark_text_in_streams(
    input_pdf: Path,
    output_pdf: Path,
    watermark_texts: list[str],
) -> tuple[int, int]:
    doc = fitz.open(input_pdf)
    updated_streams = 0

    for xref in range(1, doc.xref_length()):
        try:
            stream = doc.xref_stream(xref)
        except Exception:
            continue

        if not stream:
            continue

        updated = stream
        for watermark_text in watermark_texts:
            target = f"({watermark_text})".encode("latin1", errors="ignore")
            updated = updated.replace(target, b"()")

        if updated != stream:
            doc.update_stream(xref, updated)
            updated_streams += 1

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True)
    page_count = doc.page_count
    doc.close()
    return page_count, updated_streams


def main() -> None:
    pdf_files = iter_pdf_files(INPUT_FOLDER)
    if not pdf_files:
        print(f"No PDF files found in: {INPUT_FOLDER}")
        sys.exit(1)

    processed = 0
    for pdf_file in pdf_files:
        output_pdf = build_output_path(pdf_file)
        try:
            pages, updated_streams = replace_watermark_text_in_streams(
                pdf_file,
                output_pdf,
                WATERMARK_TEXTS,
            )
            processed += 1
            print(
                f"Removed watermark text: {pdf_file.name} | pages: {pages} | streams updated: {updated_streams}"
            )
            print(f"Saved to: {output_pdf}")
        except Exception as exc:
            print(f"Failed: {pdf_file.name} ({exc})")

    print(f"Finished. Total PDFs processed: {processed}")


if __name__ == "__main__":
    main()
