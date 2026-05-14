from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

try:
    import pymupdf
except ImportError:  # pragma: no cover - compatibility with older PyMuPDF releases
    import fitz as pymupdf  # type: ignore[no-redef]


VALID_DPI_RANGE = range(72, 1201)
VALID_QUALITY_RANGE = range(1, 101)


@dataclass(frozen=True)
class ConversionOptions:
    dpi: int = 300
    jpeg_quality: int = 90
    overwrite: bool = False

    def validate(self) -> None:
        if self.dpi not in VALID_DPI_RANGE:
            raise ValueError("DPI must be between 72 and 1200.")
        if self.jpeg_quality not in VALID_QUALITY_RANGE:
            raise ValueError("JPEG quality must be between 1 and 100.")


@dataclass(frozen=True)
class ProgressEvent:
    source: Path
    page_number: int
    page_count: int
    output_path: Path | None
    status: str
    message: str


@dataclass
class FileConversionResult:
    source: Path
    page_count: int = 0
    outputs: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    error: str | None = None


@dataclass
class ConversionSummary:
    pdf_count: int = 0
    page_count: int = 0
    output_count: int = 0
    skipped_count: int = 0
    errors: list[str] = field(default_factory=list)
    results: list[FileConversionResult] = field(default_factory=list)


ProgressCallback = Callable[[ProgressEvent], None]


def discover_pdfs(paths: Iterable[Path | str]) -> list[Path]:
    pdfs: list[Path] = []

    for raw_path in paths:
        path = Path(raw_path).expanduser()
        if path.is_file() and path.suffix.lower() == ".pdf":
            pdfs.append(path)
        elif path.is_dir():
            pdfs.extend(
                child
                for child in sorted(path.iterdir(), key=lambda item: item.name.lower())
                if child.is_file() and child.suffix.lower() == ".pdf"
            )

    return _dedupe_paths(pdfs)


def convert_pdfs(
    input_paths: Iterable[Path | str],
    output_dir: Path | str,
    options: ConversionOptions | None = None,
    progress_callback: ProgressCallback | None = None,
) -> ConversionSummary:
    options = options or ConversionOptions()
    options.validate()

    output_root = Path(output_dir).expanduser()
    output_root.mkdir(parents=True, exist_ok=True)

    pdfs = discover_pdfs(input_paths)
    summary = ConversionSummary(pdf_count=len(pdfs))

    for pdf_path in pdfs:
        result = convert_pdf(pdf_path, output_root, options, progress_callback)
        summary.results.append(result)
        summary.page_count += result.page_count
        summary.output_count += len(result.outputs)
        summary.skipped_count += len(result.skipped)
        if result.error:
            summary.errors.append(f"{pdf_path.name}: {result.error}")

    return summary


def convert_pdf(
    pdf_path: Path | str,
    output_dir: Path,
    options: ConversionOptions,
    progress_callback: ProgressCallback | None = None,
) -> FileConversionResult:
    source = Path(pdf_path).expanduser()
    result = FileConversionResult(source=source)

    try:
        with pymupdf.open(source) as document:
            result.page_count = len(document)
            if result.page_count == 0:
                result.error = "PDF has no pages."
                return result

            for page_index in range(result.page_count):
                page_number = page_index + 1
                output_path = output_path_for_page(source, output_dir, result.page_count, page_number)

                if output_path.exists() and not options.overwrite:
                    result.skipped.append(output_path)
                    _emit(
                        progress_callback,
                        source,
                        page_number,
                        result.page_count,
                        output_path,
                        "skipped",
                        f"Skipped existing file: {output_path.name}",
                    )
                    continue

                page = document.load_page(page_index)
                pixmap = page.get_pixmap(dpi=options.dpi, colorspace=pymupdf.csRGB, alpha=False)
                pixmap.save(str(output_path), output="jpeg", jpg_quality=options.jpeg_quality)
                result.outputs.append(output_path)
                _emit(
                    progress_callback,
                    source,
                    page_number,
                    result.page_count,
                    output_path,
                    "converted",
                    f"Created {output_path.name}",
                )

    except Exception as exc:  # noqa: BLE001 - show user-friendly batch error and continue
        result.error = str(exc)
        _emit(progress_callback, source, 0, result.page_count, None, "error", result.error)

    return result


def output_path_for_page(source: Path, output_dir: Path, page_count: int, page_number: int) -> Path:
    if page_count == 1:
        filename = f"{source.stem}.jpg"
    else:
        filename = f"{source.stem}-page-{page_number:03d}.jpg"
    return output_dir / filename


def _emit(
    progress_callback: ProgressCallback | None,
    source: Path,
    page_number: int,
    page_count: int,
    output_path: Path | None,
    status: str,
    message: str,
) -> None:
    if progress_callback is None:
        return

    progress_callback(
        ProgressEvent(
            source=source,
            page_number=page_number,
            page_count=page_count,
            output_path=output_path,
            status=status,
            message=message,
        )
    )


def _dedupe_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique_paths: list[Path] = []

    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_paths.append(path)

    return unique_paths

