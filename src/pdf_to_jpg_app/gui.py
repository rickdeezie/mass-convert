from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from pdf_to_jpg_app.converter import ConversionOptions, ProgressEvent, convert_pdfs, discover_pdfs


class PdfToJpgApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=16)
        self.master = master
        self.input_paths: list[Path] = []
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.worker: threading.Thread | None = None

        self.output_dir_var = tk.StringVar()
        self.dpi_var = tk.IntVar(value=300)
        self.quality_var = tk.IntVar(value=90)
        self.overwrite_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Select PDFs or a folder to begin.")
        self.count_var = tk.StringVar(value="0 PDFs selected")

        self._build_ui()
        self._configure_window()

    def _configure_window(self) -> None:
        self.master.title("PDF to JPG Converter")
        self.master.minsize(760, 560)
        self.grid(row=0, column=0, sticky="nsew")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _build_ui(self) -> None:
        self._build_inputs()
        self._build_file_list()
        self._build_settings()
        self._build_progress()

    def _build_inputs(self) -> None:
        input_frame = ttk.LabelFrame(self, text="Input PDFs", padding=12)
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        button_row = ttk.Frame(input_frame)
        button_row.grid(row=0, column=0, sticky="ew")
        button_row.columnconfigure(4, weight=1)

        ttk.Button(button_row, text="Add PDF Files", command=self.add_pdf_files).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_row, text="Select Folder", command=self.select_input_folder).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_row, text="Clear", command=self.clear_inputs).grid(row=0, column=2, padx=(0, 12))
        ttk.Label(button_row, textvariable=self.count_var).grid(row=0, column=3, sticky="w")

    def _build_file_list(self) -> None:
        list_frame = ttk.Frame(self)
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 12))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.input_list = tk.Listbox(list_frame, height=8, activestyle="none")
        self.input_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.input_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.input_list.configure(yscrollcommand=scrollbar.set)

    def _build_settings(self) -> None:
        settings = ttk.LabelFrame(self, text="Output Settings", padding=12)
        settings.grid(row=2, column=0, sticky="ew")
        settings.columnconfigure(1, weight=1)

        ttk.Label(settings, text="Output folder").grid(row=0, column=0, sticky="w", padx=(0, 8))
        output_entry = ttk.Entry(settings, textvariable=self.output_dir_var)
        output_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(settings, text="Browse", command=self.select_output_folder).grid(row=0, column=2)

        values = ttk.Frame(settings)
        values.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        values.columnconfigure(6, weight=1)

        ttk.Label(values, text="DPI").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.dpi_box = ttk.Combobox(values, textvariable=self.dpi_var, values=(150, 200, 300, 600), width=8)
        self.dpi_box.grid(row=0, column=1, sticky="w", padx=(0, 24))

        ttk.Label(values, text="JPEG quality").grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.quality_spin = ttk.Spinbox(values, from_=1, to=100, textvariable=self.quality_var, width=8)
        self.quality_spin.grid(row=0, column=3, sticky="w", padx=(0, 24))

        ttk.Checkbutton(values, text="Overwrite existing files", variable=self.overwrite_var).grid(
            row=0, column=4, sticky="w"
        )

    def _build_progress(self) -> None:
        progress = ttk.Frame(self)
        progress.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        progress.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(progress, mode="determinate")
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.convert_button = ttk.Button(progress, text="Convert", command=self.start_conversion)
        self.convert_button.grid(row=0, column=1)

        ttk.Label(progress, textvariable=self.status_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        log_frame = ttk.Frame(self)
        log_frame.grid(row=4, column=0, sticky="nsew", pady=(12, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log = tk.Text(log_frame, height=8, wrap="word", state="disabled")
        self.log.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=log_scroll.set)

    def add_pdf_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Choose PDF files",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")),
        )
        self._add_inputs(Path(path) for path in paths)

    def select_input_folder(self) -> None:
        folder = filedialog.askdirectory(title="Choose input folder")
        if folder:
            self._add_inputs([Path(folder)])

    def clear_inputs(self) -> None:
        self.input_paths.clear()
        self.refresh_input_list()

    def select_output_folder(self) -> None:
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_dir_var.set(folder)

    def start_conversion(self) -> None:
        if self.worker and self.worker.is_alive():
            return

        try:
            options = self._read_options()
        except ValueError as exc:
            messagebox.showerror("Invalid settings", str(exc))
            return

        if not self.input_paths:
            messagebox.showerror("Missing input", "Choose PDF files or an input folder.")
            return

        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("Missing output folder", "Choose an output folder.")
            return

        pdfs = discover_pdfs(self.input_paths)
        if not pdfs:
            messagebox.showerror("No PDFs found", "No PDF files were found in the selected input.")
            return

        self.progress_bar.configure(maximum=len(pdfs), value=0)
        self.convert_button.configure(state="disabled")
        self.status_var.set(f"Converting {len(pdfs)} PDF files...")
        self.clear_log()

        self.worker = threading.Thread(
            target=self._run_conversion,
            args=(list(self.input_paths), Path(output_dir), options),
            daemon=True,
        )
        self.worker.start()
        self.after(100, self._process_events)

    def refresh_input_list(self) -> None:
        self.input_list.delete(0, tk.END)
        for path in self.input_paths:
            self.input_list.insert(tk.END, str(path))
        pdf_count = len(discover_pdfs(self.input_paths))
        self.count_var.set(f"{pdf_count} PDF{'s' if pdf_count != 1 else ''} selected")

    def clear_log(self) -> None:
        self.log.configure(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.configure(state="disabled")

    def log_message(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert(tk.END, f"{message}\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def _add_inputs(self, paths: object) -> None:
        existing = {path.resolve() for path in self.input_paths}
        for path in paths:
            candidate = Path(path).expanduser()
            if candidate.exists() and candidate.resolve() not in existing:
                self.input_paths.append(candidate)
                existing.add(candidate.resolve())
        self.refresh_input_list()

    def _read_options(self) -> ConversionOptions:
        try:
            dpi = int(self.dpi_var.get())
            quality = int(self.quality_var.get())
        except (tk.TclError, ValueError) as exc:
            raise ValueError("DPI and JPEG quality must be whole numbers.") from exc

        options = ConversionOptions(dpi=dpi, jpeg_quality=quality, overwrite=self.overwrite_var.get())
        options.validate()
        return options

    def _run_conversion(self, input_paths: list[Path], output_dir: Path, options: ConversionOptions) -> None:
        try:
            summary = convert_pdfs(input_paths, output_dir, options, self._queue_progress_event)
            self.events.put(("done", summary))
        except Exception as exc:  # noqa: BLE001 - report unexpected top-level UI errors
            self.events.put(("fatal", str(exc)))

    def _queue_progress_event(self, event: ProgressEvent) -> None:
        self.events.put(("progress", event))

    def _process_events(self) -> None:
        while True:
            try:
                event_type, payload = self.events.get_nowait()
            except queue.Empty:
                break

            if event_type == "progress":
                self._handle_progress_event(payload)
            elif event_type == "done":
                self._handle_done(payload)
                return
            elif event_type == "fatal":
                self._handle_fatal(str(payload))
                return

        if self.worker and self.worker.is_alive():
            self.after(100, self._process_events)

    def _handle_progress_event(self, payload: object) -> None:
        event = payload
        if not isinstance(event, ProgressEvent):
            return

        if event.status == "error":
            self.log_message(f"ERROR {event.source.name}: {event.message}")
            return

        self.log_message(f"{event.source.name} page {event.page_number}/{event.page_count}: {event.message}")
        if event.page_number == event.page_count:
            self.progress_bar.step(1)

    def _handle_done(self, payload: object) -> None:
        summary = payload
        output_count = getattr(summary, "output_count", 0)
        skipped_count = getattr(summary, "skipped_count", 0)
        errors = getattr(summary, "errors", [])

        self.convert_button.configure(state="normal")
        self.progress_bar.configure(value=self.progress_bar["maximum"])

        if errors:
            self.status_var.set(f"Done with {len(errors)} error(s). Created {output_count}, skipped {skipped_count}.")
            messagebox.showwarning("Conversion complete", self.status_var.get())
        else:
            self.status_var.set(f"Done. Created {output_count} JPG file(s), skipped {skipped_count}.")
            messagebox.showinfo("Conversion complete", self.status_var.get())

    def _handle_fatal(self, message: str) -> None:
        self.convert_button.configure(state="normal")
        self.status_var.set("Conversion failed.")
        self.log_message(f"ERROR {message}")
        messagebox.showerror("Conversion failed", message)


def main() -> None:
    root = tk.Tk()
    PdfToJpgApp(root)
    root.mainloop()

