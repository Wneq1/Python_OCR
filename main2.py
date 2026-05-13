import easyocr

from config import AppConfig
from camera_selector import choose_camera_preview_gui
from ocr_app import run_ocr_window


def main():
    """
    Główna funkcja programu.

    Tutaj ustawiasz najważniejsze parametry aplikacji.
    """

    config = AppConfig(
        # Ile kamer maksymalnie szukać
        max_cameras=10,

        # Rozdzielczość podglądu kamer w oknie wyboru
        preview_width=320,
        preview_height=240,

        # Rozdzielczość kamery używanej do OCR
        camera_width=1280,
        camera_height=720,

        # Rozmiar obrazu w głównym oknie programu
        display_width=960,
        display_height=540,

        # Co ile klatek robić OCR
        # 1 = każda klatka
        # 5 = co piątą klatkę
        # 15 = co piętnastą klatkę
        ocr_interval=1,

        # Powiększenie ROI przed OCR
        roi_scale=2.0,

        # Znaki, które OCR może rozpoznawać
        allowlist="0123456789,.",

        # Język OCR
        ocr_languages=("en",),

        # GPU
        use_gpu=True
    )

    print("Ładowanie EasyOCR...")

    reader = easyocr.Reader(
        list(config.ocr_languages),
        gpu=config.use_gpu
    )

    camera_id = choose_camera_preview_gui(config)

    if camera_id is None:
        print("Nie wybrano kamery. Program zakończony.")
        return

    print(f"Wybrano kamerę: {camera_id}")

    run_ocr_window(camera_id, reader, config)

    print("Program zakończony.")


if __name__ == "__main__":
    main()