from __future__ import annotations

from pathlib import Path

from pdfrw import PageMerge, PdfReader, PdfWriter


INPUT_FOLDER = Path("pdfs/input_pdf")
OUTPUT_FOLDER = Path("pdfs/output_pdf_modify_pdf_4up")
LEFT_RIGHT_MARGIN_SIZE = 20
TOP_BOTTOM_MARGIN_SIZE = -10
HORIZONTAL_GAP_SIZE = 2
VERTICAL_GAP_SIZE = 2

# A4 size in points.
A4_WIDTH = 595
A4_HEIGHT = 842


def iter_pdf_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.iterdir() if path.suffix.lower() == ".pdf")


def build_output_path(input_pdf: Path, output_folder: Path) -> Path:
    return output_folder / input_pdf.name


def get_page_size(page) -> tuple[float, float]:
    media_box = page.MediaBox
    width = float(media_box[2]) - float(media_box[0])
    height = float(media_box[3]) - float(media_box[1])
    return width, height


def add_page_to_slot(
    blank_page,
    source_page,
    slot_x,
    slot_y,
    slot_width,
    slot_height,
    vertical_align: str = "center",
) -> None:
    orig_width, orig_height = get_page_size(source_page)

    width_scale = slot_width / orig_width
    height_scale = slot_height / orig_height
    scale = min(width_scale, height_scale)

    scaled_width = orig_width * scale
    scaled_height = orig_height * scale

    x_pos = slot_x + (slot_width - scaled_width) / 2
    if vertical_align == "top":
        y_pos = slot_y + slot_height - scaled_height
    elif vertical_align == "bottom":
        y_pos = slot_y
    else:
        y_pos = slot_y + (slot_height - scaled_height) / 2

    placed = PageMerge().add(source_page)[0]
    placed.x = x_pos
    placed.y = y_pos
    placed.scale(scale)
    blank_page.add(placed)


def merge_pdf_four_up(
    input_path: Path | str,
    output_path: Path | str,
    left_right_margin: int = LEFT_RIGHT_MARGIN_SIZE,
    top_bottom_margin: int = TOP_BOTTOM_MARGIN_SIZE,
    horizontal_gap: int = HORIZONTAL_GAP_SIZE,
    vertical_gap: int = VERTICAL_GAP_SIZE,
) -> None:
    """
    Merge four PDF pages onto one A4 page in a 2x2 layout:

    1 2
    3 4
    """
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    left_margin = left_right_margin
    right_margin = left_right_margin
    usable_width = A4_WIDTH - left_margin - right_margin - horizontal_gap
    usable_height = A4_HEIGHT - (2 * top_bottom_margin) - vertical_gap
    slot_width = usable_width / 2
    slot_height = usable_height / 2

    for i in range(0, len(reader.pages), 4):
        blank = PageMerge()
        blank.mbox = [0, 0, A4_WIDTH, A4_HEIGHT]

        slots = [
            (left_margin, top_bottom_margin + slot_height + vertical_gap),  # top-left
            (left_margin + slot_width + horizontal_gap, top_bottom_margin + slot_height + vertical_gap),  # top-right
            (left_margin, top_bottom_margin),  # bottom-left
            (left_margin + slot_width + horizontal_gap, top_bottom_margin),  # bottom-right
        ]

        for offset, (slot_x, slot_y) in enumerate(slots):
            page_index = i + offset
            if page_index >= len(reader.pages):
                break
            vertical_align = "bottom" if offset < 2 else "top"
            add_page_to_slot(
                blank,
                reader.pages[page_index],
                slot_x,
                slot_y,
                slot_width,
                slot_height,
                vertical_align=vertical_align,
            )

        writer.addpage(blank.render())

    writer.write(str(output_path))


def process_pdf_folder(
    input_folder: Path,
    output_folder: Path,
    left_right_margin: int = LEFT_RIGHT_MARGIN_SIZE,
    top_bottom_margin: int = TOP_BOTTOM_MARGIN_SIZE,
    horizontal_gap: int = HORIZONTAL_GAP_SIZE,
    vertical_gap: int = VERTICAL_GAP_SIZE,
) -> Path:
    """
    Process all PDFs in the input folder and save 4-up versions to the output folder.
    """
    output_folder.mkdir(parents=True, exist_ok=True)

    processed_files = 0
    for pdf_file in iter_pdf_files(input_folder):
        output_file = build_output_path(pdf_file, output_folder)
        print(f"Processing: {pdf_file.name}")
        try:
            merge_pdf_four_up(
                pdf_file,
                output_file,
                left_right_margin=left_right_margin,
                top_bottom_margin=top_bottom_margin,
                horizontal_gap=horizontal_gap,
                vertical_gap=vertical_gap,
            )
            processed_files += 1
            print(f"Created: {output_file.name}")
        except Exception as exc:
            print(f"Error processing {pdf_file.name}: {exc}")

    print(f"\nProcessing complete! {processed_files} PDFs created in: {output_folder}")
    return output_folder


if __name__ == "__main__":
    process_pdf_folder(
        INPUT_FOLDER,
        OUTPUT_FOLDER,
        LEFT_RIGHT_MARGIN_SIZE,
        TOP_BOTTOM_MARGIN_SIZE,
        HORIZONTAL_GAP_SIZE,
        VERTICAL_GAP_SIZE,
    )
