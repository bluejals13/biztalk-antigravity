import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routers import convert

app = FastAPI(
    title="업무 말투 변환기 API (BizTalk Tone Converter)",
    description="Upstage Solar-Pro3 모델 기반 텍스트 말투 변환 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(convert.router, prefix="/api")

# 헬스 체크 엔드포인트
@app.get("/health", summary="서버 헬스 체크")
async def health_check():
    return {"status": "ok"}

# 프론트엔드 정적 파일 마운트
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

