import cv2


def open_camera(camera_id, width=None, height=None):
    """
    Próbuje otworzyć kamerę kilkoma backendami OpenCV.

    camera_id:
        Numer kamery, np. 0, 1, 2.

    width, height:
        Opcjonalna rozdzielczość kamery.
    """

    backends = [
        cv2.CAP_DSHOW,
        cv2.CAP_MSMF,
        cv2.CAP_ANY
    ]

    for backend in backends:
        cap = cv2.VideoCapture(camera_id, backend)

        if width is not None:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)

        if height is not None:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if cap.isOpened():
            ret, frame = cap.read()

            if ret and frame is not None:
                return cap

        cap.release()

    return None