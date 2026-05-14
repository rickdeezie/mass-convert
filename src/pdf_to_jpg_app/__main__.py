import multiprocessing as mp


def main() -> None:
    from pdf_to_jpg_app.gui import main as gui_main

    gui_main()


if __name__ == "__main__":
    mp.freeze_support()
    main()
