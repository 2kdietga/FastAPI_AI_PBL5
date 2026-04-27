import math
import numpy as np


def _point_to_np(point):
    """
    MediaPipe landmark có x, y, z.
    EAR chỉ cần x, y là đủ.
    """
    return np.array([point.x, point.y], dtype=np.float32)


def _distance(p1, p2):
    return float(np.linalg.norm(_point_to_np(p1) - _point_to_np(p2)))


def _eye_aspect_ratio(landmarks, eye_indices):
    """
    EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
    eye_indices = [p1, p2, p3, p4, p5, p6]
    """
    p1, p2, p3, p4, p5, p6 = eye_indices

    vertical_1 = _distance(landmarks[p2], landmarks[p6])
    vertical_2 = _distance(landmarks[p3], landmarks[p5])
    horizontal = _distance(landmarks[p1], landmarks[p4])

    if horizontal == 0:
        return 0.0

    return float((vertical_1 + vertical_2) / (2.0 * horizontal))


def get_ear(landmarks):
    """
    Tính Eye Aspect Ratio trung bình của 2 mắt.

    Index theo MediaPipe Face Mesh / Face Landmarker:
    - Left eye: 33, 160, 158, 133, 153, 144
    - Right eye: 362, 385, 387, 263, 373, 380
    """

    left_eye = [33, 160, 158, 133, 153, 144]
    right_eye = [362, 385, 387, 263, 373, 380]

    left_ear = _eye_aspect_ratio(landmarks, left_eye)
    right_ear = _eye_aspect_ratio(landmarks, right_eye)

    return float((left_ear + right_ear) / 2.0)


def get_head_yaw(transformation_matrix):
    """
    Tính yaw từ facial_transformation_matrixes của MediaPipe.

    yaw > 0  : quay sang phải
    yaw < 0  : quay sang trái
    yaw ~= 0 : nhìn thẳng

    Trả về đơn vị độ.
    """

    matrix = np.array(transformation_matrix, dtype=np.float32)

    if matrix.size == 16:
        matrix = matrix.reshape(4, 4)

    if matrix.shape[0] < 3 or matrix.shape[1] < 3:
        return 0.0

    rotation = matrix[:3, :3]

    # yaw quanh trục Y
    yaw_rad = math.atan2(
        -rotation[2, 0],
        math.sqrt(rotation[0, 0] ** 2 + rotation[1, 0] ** 2),
    )

    yaw_deg = math.degrees(yaw_rad)

    return float(yaw_deg)