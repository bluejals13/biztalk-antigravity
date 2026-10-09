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

# --- 정적 파일(프론트엔ed) 서빙 ---
# 현재 파일(main.py)이 app 폴더 안에 있으므로, parent는 app, parent.parent는 FastApi(루트)가 됩니다.
# 만약 frontend 폴더가 FastApi 바로 아래에 있다면 아래와 같이 잡아야 정확합니다.
frontend_path = Path(__file__).resolve().parent.parent / "frontend"

# 폴더 존재 여부 확인 및 마운트
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"✅ 프론트엔드 경로 연결 완료: {frontend_path}")
else:
    print(f"⚠️ 경고: {frontend_path} 폴더를 찾을 수 없습니다. FastApi 폴더 내부에 'frontend' 폴더를 생성해주세요.")


