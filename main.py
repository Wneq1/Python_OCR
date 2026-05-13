from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Nie udało się otworzyć kamerki.")
    exit()

window_name = "YOLO z dynamicznym ROI"

try:
    # Pobranie pierwszej klatki
    ret, frame = cap.read()

    if not ret:
        print("Nie udało się pobrać pierwszej klatki.")
        exit()

    # Wybór ROI
    roi_box = cv2.selectROI("Wybierz ROI", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Wybierz ROI")

    x, y, w, h = roi_box

    if w == 0 or h == 0:
        print("Nie wybrano ROI.")
        exit()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Nie udało się pobrać obrazu z kamerki.")
            break

        roi = frame[y:y+h, x:x+w]

        results = model(roi, verbose=False)

        annotated_roi = results[0].plot()

        frame[y:y+h, x:x+w] = annotated_roi

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(
            frame,
            "ROI",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF

        # Q - wyjście
        if key == ord("q"):
            break

        # R - ponowny wybór ROI
        if key == ord("r"):
            roi_box = cv2.selectROI("Wybierz ROI", frame, fromCenter=False, showCrosshair=True)
            cv2.destroyWindow("Wybierz ROI")

            new_x, new_y, new_w, new_h = roi_box

            if new_w != 0 and new_h != 0:
                x, y, w, h = new_x, new_y, new_w, new_h
            else:
                print("Nie wybrano nowego ROI, zostaje poprzedni.")

        # Kliknięcie X w oknie
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

except KeyboardInterrupt:
    print("Przerwano program z klawiatury.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Program zakończony.")