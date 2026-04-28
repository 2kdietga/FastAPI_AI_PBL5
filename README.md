# FastAPI AI - Driver Monitoring AI Server

Service FastAPI nay phu trach xu ly anh tu camera/thiet bi de ho tro he thong giam sat tai xe. Ung dung nhan tung frame anh, phat hien khuon mat bang MediaPipe Face Landmarker, tinh chi so mat nham va goc quay dau, sau do tra ve trang thai de backend chinh co the ghi nhan vi pham.

## Muc luc

- [Chuc nang chinh](#chuc-nang-chinh)
- [Cong nghe su dung](#cong-nghe-su-dung)
- [Cau truc du an](#cau-truc-du-an)
- [Cach hoat dong](#cach-hoat-dong)
- [API endpoints](#api-endpoints)
- [Bien moi truong](#bien-moi-truong)
- [Cai dat va chay local](#cai-dat-va-chay-local)
- [Chay bang Docker](#chay-bang-docker)
- [Tich hop voi backend khac](#tich-hop-voi-backend-khac)
- [Ghi chu van hanh](#ghi-chu-van-hanh)

## Chuc nang chinh

- Kiem tra service qua endpoint `/health`.
- Nhan anh qua multipart form data tai endpoint `/v1/analyze/`.
- Bao ve endpoint phan tich bang header `x-ai-service-token`.
- Doc anh tu bytes, chuyen doi qua OpenCV/Numpy/Pillow.
- Dung MediaPipe Face Landmarker de phat hien landmark khuon mat va ma tran bien doi khuon mat.
- Tinh EAR (Eye Aspect Ratio) cho hai mat de nhan dien mat nham.
- Tu dong calibration EAR rieng cho tung `device_key`.
- Theo doi chuoi frame mat nham de phat hien buon ngu/ngu gat.
- Tinh goc yaw cua dau de phat hien tai xe quay trai/quay phai qua nguong.
- Luu state rieng theo `device_key`, phu hop khi nhieu thiet bi gui anh ve cung mot AI server.
- Co Dockerfile de deploy len moi truong container, mac dinh chay cong `8001`.

## Cong nghe su dung

- Python 3.10
- FastAPI
- Uvicorn
- Pydantic Settings
- MediaPipe
- OpenCV
- Numpy
- Pillow
- python-multipart

Danh sach dependency day du nam trong file `requirements.txt`.

## Cau truc du an

```text
FastAPI_AI/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── security.py
│   ├── schemas.py
│   └── ai/
│       ├── __init__.py
│       ├── engine.py
│       ├── mediapipe_loader.py
│       ├── metrics.py
│       ├── state.py
│       └── models/
│           └── face_landmarker.task
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

### Vai tro tung file chinh

| File | Vai tro |
| --- | --- |
| `app/main.py` | Khoi tao FastAPI app va khai bao endpoint `/health`, `/v1/analyze/`. |
| `app/config.py` | Quan ly cau hinh bang `pydantic-settings`, doc bien tu `.env`. |
| `app/security.py` | Kiem tra token noi bo qua header `x-ai-service-token`. |
| `app/schemas.py` | Khai bao schema response tham khao cho ket qua phan tich. |
| `app/ai/engine.py` | Xu ly anh, goi MediaPipe, tinh trang thai mat/dau va tra ket qua. |
| `app/ai/metrics.py` | Tinh EAR va yaw cua dau. |
| `app/ai/state.py` | Luu state theo tung `device_key`: calibration, streak mat nham, diem quay dau. |
| `app/ai/mediapipe_loader.py` | Tai model neu thieu va khoi tao singleton Face Landmarker. |
| `app/ai/models/face_landmarker.task` | Model MediaPipe Face Landmarker dang co san trong repo. |
| `Dockerfile` | Dong goi ung dung voi Python slim va cac thu vien he thong can cho OpenCV/MediaPipe. |

## Cach hoat dong

### 1. Request vao endpoint phan tich

Client gui request `POST /v1/analyze/` gom:

- Anh trong field `image`.
- Ma thiet bi trong field `device_key`.
- Ma the trong field `card_uid` neu co.
- Header `x-ai-service-token` de xac thuc noi bo.

### 2. Doc va chuan hoa anh

`app/ai/engine.py` doc bytes bang Pillow, chuyen anh sang RGB/BGR bang Numpy va OpenCV, sau do tao `mp.Image` de dua vao MediaPipe.

### 3. Phat hien khuon mat

MediaPipe Face Landmarker duoc khoi tao mot lan trong `app/ai/mediapipe_loader.py` va duoc tai su dung cho cac request sau.

Neu file model khong ton tai tai duong dan `MEDIAPIPE_MODEL_PATH`, service se tu tai model tu Google Storage:

```text
https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

Trong repo hien tai da co file:

```text
app/ai/models/face_landmarker.task
```

### 4. Xu ly khi khong thay khuon mat

Neu khong co landmark khuon mat hoac khong co facial transformation matrix, service tra ve trang thai:

```text
NO_FACE
```

Dong thoi reset mot so state lien quan den mat nham, giam dan diem quay dau, va khong tao vi pham moi.

### 5. Phat hien quay dau

Service tinh yaw tu `facial_transformation_matrixes` cua MediaPipe:

- `yaw > 0`: quay sang phai.
- `yaw < 0`: quay sang trai.
- Gan `0`: nhin thang.

Neu yaw vuot nguong `DROWSINESS_HEAD_YAW_THRESHOLD`, `head_turn_score` tang len. Khi score dat `DROWSINESS_HEAD_TURN_VIOLATION_FRAMES` va truoc do chua o trang thai vi pham, response se bat co:

```json
{
  "should_create_head_turn_violation": true
}
```

Trang thai dau co the la:

- `SAFE`: an toan.
- `TURNING`: dang quay dau nhung chua du nguong vi pham.
- `VIOLATION`: da du nguong quay dau vi pham.

### 6. Calibration mat

Voi moi `device_key`, service can mot so frame dau tien de lay baseline EAR. So frame calibration duoc cau hinh bang:

```text
DROWSINESS_CALIB_FRAMES
```

Trong thoi gian nay response co:

```text
CALIBRATING
```

Sau khi du frame, baseline EAR duoc tinh bang median cua danh sach EAR da thu thap.

### 7. Phat hien mat nham/buon ngu

EAR duoc tinh trung binh cho hai mat bang cac landmark cua MediaPipe Face Mesh:

- Mat trai: `33, 160, 158, 133, 153, 144`
- Mat phai: `362, 385, 387, 263, 373, 380`

Mat duoc xem la nham neu thoa mot trong hai dieu kien:

```text
ear < baseline_ear * DROWSINESS_EYE_CLOSED_RATIO
hoac
ear < DROWSINESS_EYE_CLOSED_ABS
```

Neu so frame mat nham lien tiep dat `DROWSINESS_EYE_CLOSED_FRAMES`, response se bat co:

```json
{
  "should_create_violation": true
}
```

Co nay chi bat o thoi diem bat dau vi pham moi. Khi mat mo lai, state ngu se duoc reset.

## API endpoints

### GET `/health`

Dung de kiem tra server con song hay khong.

Response mau:

```json
{
  "ok": true,
  "service": "driver-monitoring-ai-server"
}
```

Lenh kiem tra:

```bash
curl http://localhost:8001/health
```

### POST `/v1/analyze/`

Phan tich mot frame anh.

Headers:

| Header | Bat buoc | Mo ta |
| --- | --- | --- |
| `x-ai-service-token` | Co | Token noi bo, phai trung voi `AI_SERVICE_TOKEN`. |

Form data:

| Field | Kieu | Bat buoc | Mo ta |
| --- | --- | --- | --- |
| `image` | File | Co | Anh frame can phan tich. |
| `device_key` | String | Co | Ma thiet bi/camera, dung de tach state. |
| `card_uid` | String | Khong | Ma the/nguoi lai, mac dinh rong. |

Vi du voi `curl`:

```bash
curl -X POST "http://localhost:8001/v1/analyze/" \
  -H "x-ai-service-token: dev-ai-secret-token" \
  -F "image=@frame.jpg" \
  -F "device_key=device-001" \
  -F "card_uid=card-abc"
```

Vi du voi PowerShell:

```powershell
curl.exe -X POST "http://localhost:8001/v1/analyze/" `
  -H "x-ai-service-token: dev-ai-secret-token" `
  -F "image=@frame.jpg" `
  -F "device_key=device-001" `
  -F "card_uid=card-abc"
```

Response mau khi dang calibration:

```json
{
  "ok": true,
  "status": "CALIBRATING",
  "should_create_violation": false,
  "should_create_head_turn_violation": false,
  "eye_closed_streak": 0,
  "ear": 0.31,
  "baseline_ear": null,
  "is_calibrated": false,
  "head_yaw": 2.5,
  "head_direction": "FORWARD",
  "head_turn_score": 0,
  "head_status": "SAFE",
  "drowsiness_frames_count": 0,
  "head_turn_frames_count": 0,
  "device_key": "device-001",
  "card_uid": "card-abc"
}
```

Response mau khi mat dang mo:

```json
{
  "ok": true,
  "status": "EYE_OPEN",
  "should_create_violation": false,
  "should_create_head_turn_violation": false,
  "eye_closed_streak": 0,
  "ear": 0.32,
  "baseline_ear": 0.34,
  "is_calibrated": true,
  "head_yaw": 1.2,
  "head_direction": "FORWARD",
  "head_turn_score": 0,
  "head_status": "SAFE",
  "drowsiness_frames_count": 0,
  "head_turn_frames_count": 0,
  "device_key": "device-001",
  "card_uid": "card-abc"
}
```

Response mau khi can tao vi pham mat nham:

```json
{
  "ok": true,
  "status": "EYE_CLOSED",
  "should_create_violation": true,
  "should_create_head_turn_violation": false,
  "eye_closed_streak": 6,
  "ear": 0.18,
  "baseline_ear": 0.34,
  "is_calibrated": true,
  "head_yaw": 0.8,
  "head_direction": "FORWARD",
  "head_turn_score": 0,
  "head_status": "SAFE",
  "drowsiness_frames_count": 6,
  "head_turn_frames_count": 0,
  "device_key": "device-001",
  "card_uid": "card-abc"
}
```

Response mau khi khong thay khuon mat:

```json
{
  "ok": true,
  "status": "NO_FACE",
  "should_create_violation": false,
  "should_create_head_turn_violation": false,
  "eye_closed_streak": 0,
  "ear": null,
  "baseline_ear": 0.34,
  "is_calibrated": true,
  "head_yaw": 0.0,
  "head_direction": "FORWARD",
  "head_turn_score": 0,
  "head_status": "SAFE",
  "drowsiness_frames_count": 0,
  "head_turn_frames_count": 0,
  "device_key": "device-001",
  "card_uid": "card-abc"
}
```

### Ma loi

| HTTP status | Nguyen nhan |
| --- | --- |
| `401` | Header `x-ai-service-token` sai hoac thieu. |
| `422` | Thieu field bat buoc trong form data, vi du `image` hoac `device_key`. |
| `500` | Loi xu ly AI, doc anh, MediaPipe, model, hoac loi runtime khac. |

## Bien moi truong

Ung dung doc cau hinh tu file `.env` thong qua `pydantic-settings`.

Tao file `.env` tai thu muc goc du an:

```env
AI_SERVICE_TOKEN=dev-ai-secret-token

DROWSINESS_FPS=5
DROWSINESS_BUFFER_SECONDS=5

DROWSINESS_EYE_CLOSED_RATIO=0.85
DROWSINESS_EYE_CLOSED_ABS=0.20
DROWSINESS_EYE_CLOSED_FRAMES=6

DROWSINESS_HEAD_YAW_THRESHOLD=25.0
DROWSINESS_HEAD_TURN_VIOLATION_FRAMES=15
DROWSINESS_HEAD_TURN_DECAY=1

DROWSINESS_CALIB_FRAMES=10

MEDIAPIPE_MODEL_PATH=app/ai/models/face_landmarker.task
```

### Y nghia cac bien

| Bien | Mac dinh | Mo ta |
| --- | --- | --- |
| `AI_SERVICE_TOKEN` | `dev-ai-secret-token` | Token noi bo de bao ve API phan tich. Nen doi khi deploy. |
| `DROWSINESS_FPS` | `5` | FPS du kien cua luong frame. Hien tai duoc khai bao de cau hinh he thong, chua duoc dung truc tiep trong logic. |
| `DROWSINESS_BUFFER_SECONDS` | `5` | Thoi luong buffer du kien. Hien tai duoc khai bao de cau hinh he thong, chua duoc dung truc tiep trong logic. |
| `DROWSINESS_EYE_CLOSED_RATIO` | `0.85` | Ty le so voi baseline EAR de xem mat la nham. |
| `DROWSINESS_EYE_CLOSED_ABS` | `0.20` | Nguong EAR tuyet doi de xem mat la nham. |
| `DROWSINESS_EYE_CLOSED_FRAMES` | `6` | So frame mat nham lien tiep de tao vi pham ngu gat. |
| `DROWSINESS_HEAD_YAW_THRESHOLD` | `25.0` | Nguong yaw theo do de xem la quay trai/phai. |
| `DROWSINESS_HEAD_TURN_VIOLATION_FRAMES` | `15` | Diem/frame quay dau can dat de tao vi pham quay dau. |
| `DROWSINESS_HEAD_TURN_DECAY` | `1` | Muc giam score moi frame khi dau quay lai phia truoc. |
| `DROWSINESS_CALIB_FRAMES` | `10` | So frame dung de calibration EAR ban dau cho tung thiet bi. |
| `MEDIAPIPE_MODEL_PATH` | `app/ai/models/face_landmarker.task` | Duong dan model MediaPipe Face Landmarker. |

Khong commit file `.env` vi co the chua token hoac thong tin nhay cam. `.gitignore` da bo qua `.env` va `.env.*`.

## Cai dat va chay local

### 1. Tao moi truong ao

```powershell
python -m venv .venv
```

Kich hoat tren Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Kich hoat tren macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Cai dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Tao file `.env`

Tao file `.env` theo mau o phan [Bien moi truong](#bien-moi-truong). Toi thieu can co:

```env
AI_SERVICE_TOKEN=dev-ai-secret-token
```

### 4. Chay server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Mo tai:

```text
http://localhost:8001
```

Tai lieu tu dong cua FastAPI:

```text
http://localhost:8001/docs
http://localhost:8001/redoc
```

## Chay bang Docker

Build image:

```bash
docker build -t fastapi-ai .
```

Chay container:

```bash
docker run --rm -p 8001:8001 --env-file .env fastapi-ai
```

Kiem tra:

```bash
curl http://localhost:8001/health
```

Dockerfile dang:

- Dung image `python:3.10-slim`.
- Cai cac thu vien he thong can cho OpenCV/MediaPipe nhu `libgl1`, `libglib2.0-0`, `libgomp1`.
- Cai dependency tu `requirements.txt`.
- Copy thu muc `app`.
- Chay `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}`.

Khi deploy len nen tang nhu Render, bien `PORT` co the duoc nen tang cap san. Neu khong co `PORT`, app mac dinh chay cong `8001`.

## Tich hop voi backend khac

Backend chinh co the goi AI server theo luong:

1. Camera/thiet bi chup hoac trich frame anh.
2. Backend gui frame sang AI server bang multipart form data.
3. AI server tra ve trang thai hien tai.
4. Backend quyet dinh co tao ban ghi vi pham hay khong dua tren:
   - `should_create_violation`
   - `should_create_head_turn_violation`
5. Backend co the luu kem:
   - `device_key`
   - `card_uid`
   - `status`
   - `ear`
   - `baseline_ear`
   - `head_yaw`
   - `head_direction`
   - `head_status`

Vi du response co y nghia tao vi pham ngu gat:

```json
{
  "should_create_violation": true,
  "status": "EYE_CLOSED"
}
```

Vi du response co y nghia tao vi pham quay dau:

```json
{
  "should_create_head_turn_violation": true,
  "head_status": "VIOLATION",
  "head_direction": "LEFT"
}
```

## State theo `device_key`

`app/ai/state.py` luu state trong bien memory `_STATE_STORE`.

Moi `device_key` co mot `EyeState` rieng gom:

- `prev_ear`: EAR truoc do, dung de lam muot.
- `baseline_ear`: baseline sau calibration.
- `calib_ear_list`: danh sach EAR trong giai doan calibration.
- `is_calibrated`: da calibration xong hay chua.
- `eye_closed_streak`: so frame mat nham lien tiep.
- `is_sleeping`: dang o trang thai ngu gat hay chua.
- `head_turn_score`: diem quay dau tich luy.
- `head_direction`: `FORWARD`, `LEFT`, hoac `RIGHT`.
- `is_head_turning_violation`: da ghi nhan vi pham quay dau hay chua.
- `last_yaw`: yaw gan nhat.
- `drowsiness_frames`: buffer frame mat nham, hien chi giu noi bo de debug.
- `head_turn_frames`: buffer frame quay dau, hien chi giu noi bo de debug.

Vi state nam trong RAM:

- Restart server se mat calibration va streak hien tai.
- Neu chay nhieu replica/container, moi replica se co state rieng.
- Load balancer nen can sticky session theo `device_key` neu muon state on dinh giua cac request.

## Ghi chu van hanh

- Anh gui vao can la dinh dang Pillow doc duoc, vi du JPEG/PNG.
- Chat luong anh, anh sang, goc camera va FPS anh huong truc tiep den ket qua.
- Cac nguong trong `.env` nen duoc test voi camera thuc te.
- Frame dau tien cua moi thiet bi se uu tien calibration, nen chua nen tao vi pham dua tren `CALIBRATING`.
- Token mac dinh `dev-ai-secret-token` chi phu hop moi truong dev, can doi khi deploy.
- Endpoint `/v1/analyze/` hien bat moi exception va tra `500` voi thong diep `AI processing error: ...`.
- `schemas.py` co schema `AnalyzeResponse`, nhung endpoint hien tai tra dict truc tiep va chua gan `response_model`.

## Lenh huu ich

Chay server dev:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Kiem tra health:

```bash
curl http://localhost:8001/health
```

Test endpoint phan tich:

```bash
curl -X POST "http://localhost:8001/v1/analyze/" \
  -H "x-ai-service-token: dev-ai-secret-token" \
  -F "image=@frame.jpg" \
  -F "device_key=device-001"
```

Build Docker:

```bash
docker build -t fastapi-ai .
```

Run Docker:

```bash
docker run --rm -p 8001:8001 --env-file .env fastapi-ai
```

## Huong phat trien tiep

- Gan `response_model=AnalyzeResponse` cho endpoint `/v1/analyze/` neu muon OpenAPI schema chat che hon.
- Bo sung test cho `get_ear`, `get_head_yaw`, `verify_ai_token` va `/health`.
- Them endpoint reset state theo `device_key` neu can calibration lai thu cong.
- Luu frame vi pham ra storage neu backend can bang chung hinh anh.
- Can nhac external state store neu deploy nhieu replica.
