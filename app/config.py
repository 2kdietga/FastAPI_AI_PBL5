from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AI_SERVICE_TOKEN: str = "dev-ai-secret-token"

    DROWSINESS_FPS: int = 5
    DROWSINESS_BUFFER_SECONDS: int = 5

    DROWSINESS_EYE_CLOSED_RATIO: float = 0.85
    DROWSINESS_EYE_CLOSED_ABS: float = 0.20
    DROWSINESS_EYE_CLOSED_FRAMES: int = 6

    DROWSINESS_HEAD_YAW_THRESHOLD: float = 25.0
    DROWSINESS_HEAD_TURN_VIOLATION_FRAMES: int = 15
    DROWSINESS_HEAD_TURN_DECAY: int = 1

    DROWSINESS_CALIB_FRAMES: int = 10

    MEDIAPIPE_MODEL_PATH: str = "app/ai/models/face_landmarker.task"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()