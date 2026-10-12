import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Vercel / 클라우드 DB 환경 변수 (기본값은 로컬 테스트용 SQLite 설정 가능)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lab_history.db")

# Render나 Vercel의 일부 Postgres URL 형식을 SQLAlchemy가 호환되도록 수정 ('postgres://' -> 'postgresql://')
if DATABASE_URL.startswith("postgres://"):
  DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 엔진 및 세션 생성
if DATABASE_URL.startswith("sqlite"):
  engine = create_engine(
      DATABASE_URL, connect_args={"check_same_thread": False}
  )
else:
  engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI 의존성 주입용 함수
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()