# app/main.py
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.routes import router

app = FastAPI(
    title="AI Backend Lab",
    description="LangChain AI Workflow & Load Testing Lab",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

# API 라우터 등록
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- 정적 파일(프론트엔드) 서빙 경로 안전 장치 ---
possible_paths = [
    Path(__file__).resolve().parent.parent / "frontend",  # FastApi/frontend
    Path(__file__).resolve().parent / "frontend",          # app/frontend
    Path.cwd() / "frontend",                               # 현재 작업 디렉토리/frontend
    Path.cwd() / "FastApi" / "frontend"
]

frontend_path = None
for p in possible_paths:
    if p.exists() and p.is_dir():
        frontend_path = p
        break

# 폴더 존재 여부 확인 및 마운트
if frontend_path:
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"✅ 프론트엔드 경로 연결 완료: {frontend_path}")
else:
    print(f"⚠️ 경고: frontend 폴더를 찾을 수 없습니다. 경로들을 확인해주세요.")