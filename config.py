from dataclasses import dataclass


@dataclass
class AppConfig:
    # Ile kamer maksymalnie sprawdzać
    max_cameras: int = 10

    # Rozdzielczość podglądu w oknie wyboru kamery
    preview_width: int = 320
    preview_height: int = 240

    # Rozdzielczość kamery używanej do OCR
    camera_width: int = 1280
    camera_height: int = 720

    # Rozmiar obrazu wyświetlanego w głównym oknie aplikacji
    display_width: int = 960
    display_height: int = 540

    # Co ile klatek wykonywać OCR
    # 1 = OCR na każdej klatce, ale może mocno obciążać CPU
    # 5, 10, 15 = lżej dla komputera
    ocr_interval: int = 1

    # Powiększenie ROI przed OCR
    roi_scale: float = 2.0

    # Znaki dozwolone w OCR
    allowlist: str = "0123456789,."

    # Języki EasyOCR
    ocr_languages: tuple = ("en",)

    # Czy używać GPU
    use_gpu: bool = False