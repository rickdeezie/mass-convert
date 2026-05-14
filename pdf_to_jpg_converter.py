from pathlib import Path
import multiprocessing as mp
import sys


src_dir = Path(__file__).resolve().parent / "src"
if src_dir.exists():
    sys.path.insert(0, str(src_dir))


def main() -> None:
    from pdf_to_jpg_app.gui import main as gui_main

    gui_main()


if __name__ == "__main__":
    mp.freeze_support()
    main()
