from __future__ import annotations

from pathlib import Path
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install pymupdf")
    sys.exit(1)


INPUT_FOLDER = Path("pdfs/input_pdf")
OUTPUT_FOLDER = Path("pdfs/output_pdf_add_page_numbers")
FONT_SIZE = 11
BOTTOM_MARGIN = 28
TEXT_COLOR = (0, 0, 0)
START_NUMBER = 1


def iter_pdf_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.iterdir() if path.suffix.lower() == ".pdf")


def build_output_path(input_pdf: Path) -> Path:
    return OUTPUT_FOLDER / input_pdf.name


def add_page_number(page: fitz.Page, page_number: int) -> None:
    rect = page.rect
    label = str(page_number)
    text_height = FONT_SIZE * 2.4
    text_box = fitz.Rect(
        rect.x0,
        rect.y1 - BOTTOM_MARGIN - text_height,
        rect.x1,
        rect.y1 - BOTTOM_MARGIN + (FONT_SIZE * 0.4),
    )

    inserted_height = page.insert_textbox(
        text_box,
        label,
        fontname="helv",
        fontsize=FONT_SIZE,
        color=TEXT_COLOR,
        align=fitz.TEXT_ALIGN_CENTER,
        overlay=True,
    )

    if inserted_height < 0:
        fallback_width = fitz.get_text_length(label, fontname="helv", fontsize=FONT_SIZE)
        fallback_x = rect.x0 + (rect.width - fallback_width) / 2
        fallback_y = rect.y1 - BOTTOM_MARGIN
        page.insert_text(
            fitz.Point(fallback_x, fallback_y),
            label,
            fontname="helv",
            fontsize=FONT_SIZE,
            color=TEXT_COLOR,
            overlay=True,
        )


def add_page_numbers_to_pdf(input_pdf: Path, output_pdf: Path) -> int:
    doc = fitz.open(input_pdf)

    for index, page in enumerate(doc):
        add_page_number(page, START_NUMBER + index)

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf, garbage=4, deflate=True)
    page_count = doc.page_count
    doc.close()
    return page_count


def main() -> None:
    pdf_files = iter_pdf_files(INPUT_FOLDER)
    if not pdf_files:
        print(f"No PDF files found in: {INPUT_FOLDER}")
        sys.exit(1)

    processed = 0
    for pdf_file in pdf_files:
        output_pdf = build_output_path(pdf_file)
        try:
            pages = add_page_numbers_to_pdf(pdf_file, output_pdf)
            processed += 1
            print(f"Added page numbers: {pdf_file.name} | pages: {pages}")
            print(f"Saved to: {output_pdf}")
        except Exception as exc:
            print(f"Failed: {pdf_file.name} ({exc})")

    print(f"Finished. Total PDFs processed: {processed}")


if __name__ == "__main__":
    main()
