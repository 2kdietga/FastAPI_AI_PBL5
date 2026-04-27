from typing import Any, Optional
from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    ok: bool
    device_key: str

    status: str
    violation_detected: bool = False
    violation_type: Optional[str] = None

    confidence: float = 0.0
    message: str = ""

    eye_closed: Optional[bool] = None
    eye_closed_frames: Optional[int] = None
    yaw: Optional[float] = None
    head_direction: Optional[str] = None
    head_turn_score: Optional[float] = None

    debug: dict[str, Any] = {}