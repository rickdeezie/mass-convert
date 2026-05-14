from pathlib import Path

import pytest

try:
    import pymupdf
except ImportError:  # pragma: no cover
    import fitz as pymupdf  # type: ignore[no-redef]

from pdf_to_jpg_app.converter import ConversionOptions, ProgressEvent, convert_pdfs, discover_pdfs, output_path_for_page


def create_pdf(path: Path, page_count: int) -> None:
    document = pymupdf.open()
    for page_number in range(page_count):
        page = document.new_page(width=200, height=200)
        page.insert_text((40, 100), f"Page {page_number + 1}")
    document.save(path)
    document.close()


def test_discover_pdfs_from_folder_is_case_insensitive(tmp_path: Path) -> None:
    create_pdf(tmp_path / "a.pdf", 1)
    create_pdf(tmp_path / "b.PDF", 1)
    (tmp_path / "ignore.txt").write_text("not a pdf")

    assert [path.name for path in discover_pdfs([tmp_path])] == ["a.pdf", "b.PDF"]


def test_output_path_for_single_and_multi_page_pdf(tmp_path: Path) -> None:
    source = tmp_path / "scan.pdf"

    assert output_path_for_page(source, tmp_path, 1, 1) == tmp_path / "scan.jpg"
    assert output_path_for_page(source, tmp_path, 2, 1) == tmp_path / "scan-page-001.jpg"
    assert output_path_for_page(source, tmp_path, 2, 2) == tmp_path / "scan-page-002.jpg"


def test_convert_single_page_pdf_to_jpg(tmp_path: Path) -> None:
    input_pdf = tmp_path / "single.pdf"
    output_dir = tmp_path / "jpg"
    create_pdf(input_pdf, 1)
    events: list[ProgressEvent] = []

    summary = convert_pdfs(
        [input_pdf],
        output_dir,
        ConversionOptions(dpi=150, jpeg_quality=80),
        progress_callback=events.append,
    )

    output = output_dir / "single.jpg"
    assert summary.pdf_count == 1
    assert summary.page_count == 1
    assert summary.output_count == 1
    assert summary.skipped_count == 0
    assert summary.errors == []
    assert output.exists()
    assert [event.status for event in events] == ["file_started", "page_started", "converted"]


def test_convert_multi_page_pdf_to_numbered_jpgs(tmp_path: Path) -> None:
    input_pdf = tmp_path / "multi.pdf"
    output_dir = tmp_path / "jpg"
    create_pdf(input_pdf, 2)

    summary = convert_pdfs([input_pdf], output_dir, ConversionOptions(dpi=150, jpeg_quality=80))

    assert summary.output_count == 2
    assert (output_dir / "multi-page-001.jpg").exists()
    assert (output_dir / "multi-page-002.jpg").exists()


def test_skip_existing_output_by_default(tmp_path: Path) -> None:
    input_pdf = tmp_path / "single.pdf"
    output_dir = tmp_path / "jpg"
    output_dir.mkdir()
    create_pdf(input_pdf, 1)
    existing_output = output_dir / "single.jpg"
    existing_output.write_text("existing")

    summary = convert_pdfs([input_pdf], output_dir, ConversionOptions(dpi=150, jpeg_quality=80))

    assert summary.output_count == 0
    assert summary.skipped_count == 1
    assert existing_output.read_text() == "existing"


def test_validation_rejects_out_of_range_settings() -> None:
    with pytest.raises(ValueError):
        ConversionOptions(dpi=50).validate()

    with pytest.raises(ValueError):
        ConversionOptions(jpeg_quality=101).validate()
