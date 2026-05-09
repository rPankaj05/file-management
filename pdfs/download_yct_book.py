from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

from PIL import Image
import img2pdf


DEFAULT_BOOK_ID = 1920
DEFAULT_BASE_URL = f"https://yctbooksprime.com/ebook/{DEFAULT_BOOK_ID}/view-pdf"
DEFAULT_DETAIL_URL = f"https://yctbooksprime.com/ebook/{DEFAULT_BOOK_ID}"
DEFAULT_OUTPUT_PDF = "yct_book.pdf"
DEFAULT_MAX_PAGES = 100
SCREENSHOT_DELAY_SECONDS = 2.0  # Reduced from 4.0 for faster capture
SCREENSHOT_TOP_CROP = 120
SCREENSHOT_BOTTOM_CROP = 20
SCREEN_CAPTURE = Path("/usr/sbin/screencapture")


def fetch_url_text(url: str, timeout: float = 20.0) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def detect_total_pages(detail_url: str = DEFAULT_DETAIL_URL) -> int | None:
    try:
        body = fetch_url_text(detail_url)
    except Exception:
        return None

    matches = re.findall(r"\b(\d{1,5})\s+Pages\b", body, flags=re.IGNORECASE)
    if not matches:
        return None

    try:
        return max(int(match) for match in matches)
    except ValueError:
        return None


def open_url_in_chrome(url: str) -> None:
    """Open URL in the existing Chrome window/tab."""
    subprocess.run(
        [
            "open",
            "-a",
            "/Applications/Google Chrome.app",
            url,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def capture_main_screen(output_path: Path) -> None:
    """Capture the main screen to a file."""
    if not SCREEN_CAPTURE.exists():
        raise RuntimeError(f"screencapture was not found at: {SCREEN_CAPTURE}")

    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(3):
        try:
            subprocess.run(
                [str(SCREEN_CAPTURE), "-x", "-m", str(output_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if output_path.exists() and output_path.stat().st_size > 0:
                return
        except subprocess.CalledProcessError as exc:
            last_error = exc
        time.sleep(0.5)

    raise RuntimeError(f"Failed to capture the screen to {output_path}") from last_error


def crop_screenshot(image_path: Path, top: int = SCREENSHOT_TOP_CROP, bottom: int = SCREENSHOT_BOTTOM_CROP) -> None:
    """Crop top and bottom margins from screenshot."""
    with Image.open(image_path) as image:
        width, height = image.size
        top = max(0, min(top, height))
        bottom = max(0, min(bottom, height - top))
        cropped = image.crop((0, top, width, height - bottom)).convert("RGB")
        cropped.save(image_path)


def image_digest(image_path: Path) -> str:
    """Get SHA256 hash of image bytes to detect duplicates."""
    with Image.open(image_path) as image:
        return hashlib.sha256(image.tobytes()).hexdigest()


def combine_pngs_to_pdf(image_paths: list[Path], output_pdf: Path) -> None:
    """Combine image files into a single PDF."""
    with output_pdf.open("wb") as f:
        f.write(img2pdf.convert([str(path) for path in image_paths]))


def download_yct_book(
    base_url: str = DEFAULT_BASE_URL,
    detail_url: str = DEFAULT_DETAIL_URL,
    max_pages: int = DEFAULT_MAX_PAGES,
    output_pdf: str = DEFAULT_OUTPUT_PDF,
) -> None:
    """
    Download YCT book pages by capturing Chrome screenshots and combining into a PDF.
    
    How it works:
    1. Opens each page URL in your existing Chrome browser (preserves authentication)
    2. Waits for page to load
    3. Captures screenshot
    4. Crops UI elements (top/bottom margins)
    5. Combines all pages into a single PDF
    
    Note: Uses your existing Chrome profile, so you need to have the book open
    and be authenticated. Close Chrome before running if it interferes.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="yct_book_"))
    screenshots: list[Path] = []

    try:
        total_pages = detect_total_pages(detail_url)
        page_limit = min(total_pages, max_pages) if total_pages is not None else max_pages
        if total_pages is None:
            print(f"Could not detect total pages automatically. Falling back to max_pages={max_pages}.")
        else:
            print(f"Detected total pages: {total_pages} | using page limit: {page_limit}")

        previous_digest: str | None = None
        repeat_count = 0

        for page_num in range(1, page_limit + 1):
            page_url = f"{base_url}?pageNumber={page_num}"
            print(f"\nFetching page {page_num}/{page_limit}")
            
            # Open page in Chrome
            open_url_in_chrome(page_url)
            time.sleep(SCREENSHOT_DELAY_SECONDS)

            # Capture screenshot
            screenshot_path = temp_dir / f"page_{page_num:04d}.png"
            capture_main_screen(screenshot_path)
            crop_screenshot(screenshot_path)

            # Check if page image changed (detect end of book)
            current_digest = image_digest(screenshot_path)
            if previous_digest == current_digest:
                repeat_count += 1
                print(f"✓ Page {page_num} captured (duplicate #{repeat_count})")
            else:
                repeat_count = 0
                print(f"✓ Page {page_num} captured")
            
            previous_digest = current_digest

            # Stop if we see the same page multiple times (reached end)
            if repeat_count >= 2:
                print(f"\nStopped at page {page_num} (reached end of book)")
                break

            screenshots.append(screenshot_path)

        if screenshots:
            output_path = Path(output_pdf).resolve()
            print(f"\nCombining {len(screenshots)} pages into PDF...")
            combine_pngs_to_pdf(screenshots, output_path)
            print(f"✓ PDF saved as {output_path}")
        else:
            print("✗ No pages captured")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download YCT book pages into a PDF")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"Maximum number of pages to download (default: {DEFAULT_MAX_PAGES})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PDF,
        help=f"Output PDF path (default: {DEFAULT_OUTPUT_PDF})",
    )
    parser.add_argument(
        "--book-id",
        type=int,
        default=DEFAULT_BOOK_ID,
        help=f"YCT book ID to download (default: {DEFAULT_BOOK_ID})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    base_url = f"https://yctbooksprime.com/ebook/{args.book_id}/view-pdf"
    detail_url = f"https://yctbooksprime.com/ebook/{args.book_id}"
    download_yct_book(
        base_url=base_url,
        detail_url=detail_url,
        max_pages=args.max_pages,
        output_pdf=args.output,
    )
