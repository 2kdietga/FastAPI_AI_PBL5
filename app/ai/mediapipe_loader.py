import os
import threading
import urllib.request

import mediapipe as mp

from app.config import settings


_MODEL_LOCK = threading.Lock()
_LANDMARKER = None


def download_model_if_needed(model_path=None):
    model_path = model_path or settings.MEDIAPIPE_MODEL_PATH

    model_dir = os.path.dirname(model_path)
    if model_dir:
        os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(model_path):
        url = (
            "https://storage.googleapis.com/mediapipe-models/"
            "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
        )
        urllib.request.urlretrieve(url, model_path)

    return model_path


def get_landmarker():
    global _LANDMARKER

    if _LANDMARKER is not None:
        return _LANDMARKER

    with _MODEL_LOCK:
        if _LANDMARKER is not None:
            return _LANDMARKER

        model_path = download_model_if_needed()

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=True,
            num_faces=1,
        )

        _LANDMARKER = FaceLandmarker.create_from_options(options)

    return _LANDMARKER