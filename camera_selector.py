import cv2
import tkinter as tk
from PIL import Image, ImageTk

from camera_utils import open_camera


def choose_camera_preview_gui(config):
    """
    Wykrywa dostępne kamery i pokazuje okno z podglądem.
    Użytkownik wybiera kamerę, z której program ma pobierać obraz.
    """

    opened_cameras = []

    for camera_id in range(config.max_cameras):
        cap = open_camera(
            camera_id,
            width=config.preview_width,
            height=config.preview_height
        )

        if cap is not None:
            opened_cameras.append((camera_id, cap))

    if not opened_cameras:
        print("Nie wykryto żadnej kamery.")
        return None

    selected_camera = {"id": None}
    running = {"value": True}

    root = tk.Tk()
    root.title("Wybór kamery")
    root.geometry("780x580")
    root.resizable(False, False)

    title_label = tk.Label(
        root,
        text="Wybierz kamerę do OCR",
        font=("Arial", 16, "bold")
    )
    title_label.pack(pady=10)

    info_label = tk.Label(
        root,
        text="Kliknij przycisk pod podglądem odpowiedniej kamery.",
        font=("Arial", 10)
    )
    info_label.pack(pady=5)

    container = tk.Frame(root)
    container.pack(pady=10)

    preview_labels = {}

    def close_window():
        running["value"] = False

        for _, camera_cap in opened_cameras:
            camera_cap.release()

        root.destroy()

    def select_camera(camera_id):
        selected_camera["id"] = camera_id
        close_window()

    root.protocol("WM_DELETE_WINDOW", close_window)

    for i, (camera_id, cap) in enumerate(opened_cameras):
        row = i // 2
        col = i % 2

        camera_frame = tk.Frame(
            container,
            bd=2,
            relief="groove",
            padx=10,
            pady=10
        )
        camera_frame.grid(row=row, column=col, padx=10, pady=10)

        label_title = tk.Label(
            camera_frame,
            text=f"Kamera {camera_id}",
            font=("Arial", 12, "bold")
        )
        label_title.pack()

        preview_label = tk.Label(camera_frame)
        preview_label.pack(pady=5)

        preview_labels[camera_id] = preview_label

        button = tk.Button(
            camera_frame,
            text=f"Wybierz kamerę {camera_id}",
            command=lambda cid=camera_id: select_camera(cid),
            width=20
        )
        button.pack(pady=5)

    def update_previews():
        if not running["value"]:
            return

        for camera_id, cap in opened_cameras:
            ret, frame = cap.read()

            if ret and frame is not None:
                frame = cv2.resize(
                    frame,
                    (config.preview_width, config.preview_height)
                )

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)

                preview_labels[camera_id].configure(image=photo)
                preview_labels[camera_id].image = photo

        root.after(30, update_previews)

    update_previews()
    root.mainloop()

    return selected_camera["id"]