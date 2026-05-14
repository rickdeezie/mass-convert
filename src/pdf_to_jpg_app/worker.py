from __future__ import annotations

from multiprocessing.queues import Queue
from pathlib import Path

from pdf_to_jpg_app.converter import ConversionOptions, ProgressEvent, convert_pdfs


def run_conversion_worker(
    input_paths: list[str],
    output_dir: str,
    dpi: int,
    jpeg_quality: int,
    overwrite: bool,
    events: Queue,
) -> None:
    options = ConversionOptions(dpi=dpi, jpeg_quality=jpeg_quality, overwrite=overwrite)

    def report_progress(event: ProgressEvent) -> None:
        events.put(("progress", event))

    try:
        summary = convert_pdfs([Path(path) for path in input_paths], Path(output_dir), options, report_progress)
        events.put(("done", summary))
    except Exception as exc:  # noqa: BLE001 - preserve batch failure for the UI process
        events.put(("fatal", str(exc)))

