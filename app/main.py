from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException

from app.security import verify_ai_token
from app.ai.engine import process_frame_bytes


app = FastAPI(title="Driver Monitoring AI Server")


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "driver-monitoring-ai-server",
    }


@app.post("/v1/analyze/")
async def analyze_frame(
    image: UploadFile = File(...),
    device_key: str = Form(...),
    card_uid: str = Form(default=""),
    _: bool = Depends(verify_ai_token),
):
    try:
        image_bytes = await image.read()

        result = process_frame_bytes(
            image_bytes=image_bytes,
            device_key=device_key,
        )

        result["device_key"] = device_key
        result["card_uid"] = card_uid

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {str(e)}",
        )