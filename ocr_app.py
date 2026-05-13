import cv2
import tkinter as tk
from PIL import Image, ImageTk

from camera_utils import open_camera
from ocr_utils import recognize_digits_from_roi


def run_ocr_window(camera_id, reader, config):
    """
    Uruchamia główne okno programu:
    - pokazuje obraz z kamery,
    - pozwala zaznaczyć ROI,
    - rozpoznaje cyfry tylko w ROI,
    - pozwala zamrozić obraz klawiszem F.
    """

    cap = open_camera(
        camera_id,
        width=config.camera_width,
        height=config.camera_height
    )

    if cap is None:
        print("Nie udało się otworzyć wybranej kamery.")
        return

    root = tk.Tk()
    root.title("OCR cyfr w ROI")
    root.geometry("1100x780")

    running = {"value": True}

    roi = {
        "active": False,
        "drawing": False,
        "x1": 0,
        "y1": 0,
        "x2": 0,
        "y2": 0
    }

    result_data = {
        "text": "",
        "digits": []
    }

    last_camera_frame = {
        "frame": None
    }

    frozen = {
        "value": False,
        "frame": None
    }

    frame_counter = {
        "value": 0
    }

    title_label = tk.Label(
        root,
        text="OCR cyfr w wybranym ROI",
        font=("Arial", 16, "bold")
    )
    title_label.pack(pady=8)

    info_label = tk.Label(
        root,
        text="Zaznacz ROI myszką. F - zamroź/odmroź, R - reset ROI, Q lub ESC - wyjście.",
        font=("Arial", 10)
    )
    info_label.pack()

    video_label = tk.Label(root, bd=2, relief="groove")
    video_label.pack(pady=10)

    result_label = tk.Label(
        root,
        text="Liczba: ",
        font=("Arial", 14, "bold")
    )
    result_label.pack(pady=3)

    digits_label = tk.Label(
        root,
        text="Znaki: ",
        font=("Arial", 12)
    )
    digits_label.pack(pady=3)

    status_label = tk.Label(
        root,
        text="Status: obraz na żywo",
        font=("Arial", 11)
    )
    status_label.pack(pady=3)

    buttons_frame = tk.Frame(root)
    buttons_frame.pack(pady=8)

    def reset_roi():
        roi["active"] = False
        roi["drawing"] = False
        roi["x1"] = 0
        roi["y1"] = 0
        roi["x2"] = 0
        roi["y2"] = 0

        result_data["text"] = ""
        result_data["digits"] = []

        result_label.config(text="Liczba: ")
        digits_label.config(text="Znaki: ")

        print("ROI zresetowane.")

    def close_program():
        if not running["value"]:
            return

        running["value"] = False

        try:
            cap.release()
        except Exception:
            pass

        try:
            root.destroy()
        except Exception:
            pass

    def get_roi_from_frame(frame_original):
        """
        Przelicza ROI zaznaczone na obrazie wyświetlanym
        na współrzędne oryginalnej klatki z kamery.
        """

        if not roi["active"]:
            return None

        original_height, original_width = frame_original.shape[:2]

        scale_x = original_width / config.display_width
        scale_y = original_height / config.display_height

        x1_display = min(roi["x1"], roi["x2"])
        y1_display = min(roi["y1"], roi["y2"])
        x2_display = max(roi["x1"], roi["x2"])
        y2_display = max(roi["y1"], roi["y2"])

        x1 = int(x1_display * scale_x)
        y1 = int(y1_display * scale_y)
        x2 = int(x2_display * scale_x)
        y2 = int(y2_display * scale_y)

        x1 = max(0, min(x1, original_width - 1))
        y1 = max(0, min(y1, original_height - 1))
        x2 = max(0, min(x2, original_width))
        y2 = max(0, min(y2, original_height))

        roi_frame = frame_original[y1:y2, x1:x2]

        if roi_frame.size == 0:
            return None

        return roi_frame

    def perform_ocr(frame_original):
        """
        Wykonuje OCR tylko na zaznaczonym ROI.
        """

        roi_frame = get_roi_from_frame(frame_original)

        if roi_frame is None:
            return

        detected_text, detected_digits = recognize_digits_from_roi(
            reader,
            roi_frame,
            config
        )

        result_data["text"] = detected_text
        result_data["digits"] = detected_digits

        result_label.config(text=f"Liczba: {detected_text}")
        digits_label.config(text=f"Znaki: {' | '.join(detected_digits)}")

        if detected_text:
            print("Cała liczba:", detected_text)
            print("Znaki osobno:", detected_digits)
            print("-" * 40)

    def toggle_freeze():
        """
        Zamraża lub odmraża obraz.
        """

        if frozen["value"]:
            frozen["value"] = False
            frozen["frame"] = None
            status_label.config(text="Status: obraz na żywo")
            print("Obraz odmrożony.")

        else:
            if last_camera_frame["frame"] is not None:
                frozen["value"] = True
                frozen["frame"] = last_camera_frame["frame"].copy()
                status_label.config(text="Status: obraz zamrożony")
                print("Obraz zamrożony.")

                if roi["active"]:
                    perform_ocr(frozen["frame"])

    reset_button = tk.Button(
        buttons_frame,
        text="Reset ROI",
        command=reset_roi,
        width=15
    )
    reset_button.grid(row=0, column=0, padx=5)

    freeze_button = tk.Button(
        buttons_frame,
        text="Zamroź / Odmroź",
        command=toggle_freeze,
        width=18
    )
    freeze_button.grid(row=0, column=1, padx=5)

    close_button = tk.Button(
        buttons_frame,
        text="Zamknij",
        command=close_program,
        width=15
    )
    close_button.grid(row=0, column=2, padx=5)

    def on_mouse_down(event):
        roi["drawing"] = True
        roi["active"] = False

        roi["x1"] = event.x
        roi["y1"] = event.y
        roi["x2"] = event.x
        roi["y2"] = event.y

    def on_mouse_move(event):
        if roi["drawing"]:
            roi["x2"] = event.x
            roi["y2"] = event.y

    def on_mouse_up(event):
        roi["drawing"] = False

        roi["x2"] = event.x
        roi["y2"] = event.y

        x1 = min(roi["x1"], roi["x2"])
        y1 = min(roi["y1"], roi["y2"])
        x2 = max(roi["x1"], roi["x2"])
        y2 = max(roi["y1"], roi["y2"])

        if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
            roi["x1"] = x1
            roi["y1"] = y1
            roi["x2"] = x2
            roi["y2"] = y2
            roi["active"] = True

            result_data["text"] = ""
            result_data["digits"] = []

            result_label.config(text="Liczba: ")
            digits_label.config(text="Znaki: ")

            print(f"Wybrane ROI: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

            if frozen["value"] and frozen["frame"] is not None:
                perform_ocr(frozen["frame"])

        else:
            roi["active"] = False
            print("ROI za małe — zaznacz większy obszar.")

    def on_key(event):
        key = event.keysym.lower()

        if key == "r":
            reset_roi()

        elif key == "f":
            toggle_freeze()

        elif key == "q" or key == "escape":
            close_program()

    video_label.bind("<ButtonPress-1>", on_mouse_down)
    video_label.bind("<B1-Motion>", on_mouse_move)
    video_label.bind("<ButtonRelease-1>", on_mouse_up)

    root.bind("<Key>", on_key)
    root.protocol("WM_DELETE_WINDOW", close_program)

    def update_frame():
        if not running["value"]:
            return

        if frozen["value"] and frozen["frame"] is not None:
            frame = frozen["frame"].copy()

        else:
            ret, frame = cap.read()

            if not ret or frame is None:
                print("Nie udało się pobrać klatki z kamery.")
                close_program()
                return

            last_camera_frame["frame"] = frame.copy()

        frame_counter["value"] += 1

        frame_original = frame.copy()

        display_frame = cv2.resize(
            frame,
            (config.display_width, config.display_height)
        )

        if frozen["value"]:
            cv2.putText(
                display_frame,
                "ZAMROZONY OBRAZ",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3
            )

        if roi["active"] or roi["drawing"]:
            x1 = min(roi["x1"], roi["x2"])
            y1 = min(roi["y1"], roi["y2"])
            x2 = max(roi["x1"], roi["x2"])
            y2 = max(roi["y1"], roi["y2"])

            cv2.rectangle(
                display_frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                display_frame,
                "ROI",
                (x1, max(25, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        if roi["active"] and frame_counter["value"] % config.ocr_interval == 0:
            perform_ocr(frame_original)

        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(display_frame)
        photo = ImageTk.PhotoImage(image=image)

        video_label.configure(image=photo)
        video_label.image = photo

        root.after(10, update_frame)

    update_frame()
    root.mainloop()