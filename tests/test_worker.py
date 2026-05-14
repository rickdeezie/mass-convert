from pathlib import Path
import multiprocessing as mp
import queue

try:
    import pymupdf
except ImportError:  # pragma: no cover
    import fitz as pymupdf  # type: ignore[no-redef]

from pdf_to_jpg_app.worker import run_conversion_worker


def create_pdf(path: Path) -> None:
    document = pymupdf.open()
    page = document.new_page(width=200, height=200)
    page.insert_text((40, 100), "Worker test")
    document.save(path)
    document.close()


def test_spawned_worker_converts_pdf_and_reports_progress(tmp_path: Path) -> None:
    input_pdf = tmp_path / "worker.pdf"
    output_dir = tmp_path / "jpg"
    create_pdf(input_pdf)

    context = mp.get_context("spawn")
    events = context.Queue()
    process = context.Process(
        target=run_conversion_worker,
        args=([str(input_pdf)], str(output_dir), 150, 80, False, events),
    )

    process.start()
    process.join(timeout=20)

    if process.is_alive():
        process.terminate()
        process.join(timeout=5)

    assert process.exitcode == 0
    assert (output_dir / "worker.jpg").exists()

    statuses: list[str] = []
    while True:
        try:
            event_type, payload = events.get_nowait()
        except queue.Empty:
            break

        if event_type == "progress":
            statuses.append(payload.status)
        elif event_type == "done":
            statuses.append("done")

    assert "file_started" in statuses
    assert "page_started" in statuses
    assert "converted" in statuses
    assert "done" in statuses

