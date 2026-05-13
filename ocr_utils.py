import cv2
import re


def preprocess_roi_for_ocr(roi_frame, config):
    """
    Przygotowuje wycięty ROI do OCR:
    - powiększa obraz,
    - zamienia na skalę szarości,
    - lekko odszumia.
    """

    roi_big = cv2.resize(
        roi_frame,
        None,
        fx=config.roi_scale,
        fy=config.roi_scale
    )

    gray = cv2.cvtColor(roi_big, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    return gray


def clean_ocr_text(text):
    """
    Czyści tekst OCR.
    Zostawia tylko cyfry, przecinek i kropkę.
    """

    return re.sub(r"[^0-9,.]", "", text)


def recognize_digits_from_roi(reader, roi_frame, config):
    """
    Wykonuje OCR na ROI i zwraca:
    - całą rozpoznaną liczbę,
    - listę znaków osobno.
    """

    processed_roi = preprocess_roi_for_ocr(roi_frame, config)

    results = reader.readtext(
        processed_roi,
        allowlist=config.allowlist,
        detail=1,
        paragraph=False
    )

    detected_texts = []

    for bbox, text, confidence in results:
        cleaned = clean_ocr_text(text)

        if cleaned:
            detected_texts.append(cleaned)

    detected_text = "".join(detected_texts)
    detected_digits = list(detected_text)

    return detected_text, detected_digits