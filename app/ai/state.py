from dataclasses import dataclass, field
from collections import deque
from threading import Lock


@dataclass
class EyeState:
    prev_ear: float | None = None

    baseline_ear: float | None = None
    calib_ear_list: list[float] = field(default_factory=list)
    is_calibrated: bool = False

    eye_closed_streak: int = 0
    is_sleeping: bool = False

    head_turn_score: int = 0
    head_direction: str = "FORWARD"
    is_head_turning_violation: bool = False
    last_yaw: float = 0.0

    # FastAPI không trả các frame này về Django nữa.
    # Giữ lại nếu sau này bạn muốn debug nội bộ.
    drowsiness_frames: deque = field(default_factory=lambda: deque(maxlen=30))
    head_turn_frames: deque = field(default_factory=lambda: deque(maxlen=30))


_STATE_STORE = {}
_STATE_LOCK = Lock()


def get_state(device_key):
    device_key = str(device_key)

    with _STATE_LOCK:
        if device_key not in _STATE_STORE:
            _STATE_STORE[device_key] = EyeState()

        return _STATE_STORE[device_key]