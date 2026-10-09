# app/main.py
from fastapi import FastAPI
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

# API 라우터 등록
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- 정적 파일(프론트엔드) 서빙 ---
# 프론트엔드 폴더 절대 경로 설정
frontend_path = Path("../biztalk-antigravity/Frontend").resolve()

# 폴더 통째로 마운트 (html=True 옵션으로 인해 '/' 접속 시 자동으로 index.html을 찾음)
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"⚠️ 경고: {frontend_path} 폴더를 찾을 수 없습니다.")