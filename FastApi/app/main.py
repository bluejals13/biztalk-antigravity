# app/main.py
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.routes import router

import os

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

print(f"🔍 [DEBUG] current_dir: {current_dir}")
print(f"🔍 [DEBUG] root_dir: {root_dir}")
print(f"🔍 [DEBUG] root_dir contents: {os.listdir(root_dir) if root_dir.exists() else 'Not found'}")
print(f"🔍 [DEBUG] cwd contents: {os.listdir(Path.cwd())}")

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
    print(f"🔍 [DEBUG] Checking: {p} -> Exists: {exists}")
    if exists:
        frontend_path = p
        break

if frontend_path:
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    print(f"✅ 프론트엔드 경로 연결 완료: {frontend_path}")
else:
    print(f"❌ [ERROR] 모든 후보 경로에서 frontend 폴더를 찾지 못했습니다.")

