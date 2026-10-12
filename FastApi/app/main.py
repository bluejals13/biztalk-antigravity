# app/main.py
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.routes import router

from app.database import engine
from app.models import Base
from sqlalchemy import inspect

import os

# DB 테이블 존재 여부 검사 및 안내 메시지 출력
inspector = inspect(engine)
table_exists = inspector.has_table("history_records")

if not table_exists:
    print("⚠️ [DB 경고] 'history_records' 테이블이 존재하지 않습니다. 새로 생성합니다.")
else:
    print("✅ [DB 정보] 기존 'history_records' 테이블을 성공적으로 불러왔습니다.")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Backend Lab",
    description="LangChain AI Workflow & Load Testing Lab",
    version="0.1.0"
)

current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent

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

# Vercel 환경에서 생길 수 있는 모든 후보 경로
possible_paths = [
    root_dir / "frontend",
    current_dir / "frontend",
    Path.cwd() / "frontend",
    Path.cwd() / "FastApi" / "frontend",
    Path("/var/task/frontend"),
    Path("/var/task/FastApi/frontend")
]

frontend_path = None
for p in possible_paths:
    exists = p.exists() and p.is_dir()
    if exists:
        frontend_path = p
        break

if frontend_path:
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    print(f"✅ 프론트엔드 경로 연결 완료: {frontend_path}")
else:
    print(f"❌ [ERROR] 모든 후보 경로에서 frontend 폴더를 찾지 못했습니다.")