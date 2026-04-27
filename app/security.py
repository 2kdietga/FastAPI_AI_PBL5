from fastapi import Header, HTTPException
from app.config import settings


def verify_ai_token(x_ai_service_token: str = Header(default="")):
    if x_ai_service_token != settings.AI_SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid AI service token")

    return True