# core/file_history.py
from app.database import SessionLocal
from app.models import HistoryRecord
from datetime import datetime
import uuid

MAX_HISTORY_COUNT = 20  # 최대 유지 개수


def save_file_history(
    task_type: str, provider: str, input_data: str, result_data: str
) -> str:
  """DB에 기록을 저장하며, 최대 20개를 초과하면 가장 오래된 기록을 삭제합니다."""
  db = SessionLocal()
  try:
    # 1. 개수가 20개 이상인지 확인하고 초과분(가장 오래된 것) 삭제
    count = db.query(HistoryRecord).count()
    if count >= MAX_HISTORY_COUNT:
      # 생성일이 가장 오래된 항목들 조회해서 초과된 만큼 삭제
      oldest_records = (
          db.query(HistoryRecord)
          .order_by(HistoryRecord.created_at.asc())
          .limit(count - MAX_HISTORY_COUNT + 1)
          .all()
      )
      for old_rec in oldest_records:
        db.delete(old_rec)
      db.commit()

    # 2. 새로운 히스토리 생성 (기존 파일명 규칙인 uuid 혹은 타임스탬프 활용)
    record_id = (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:17]}_{task_type}"
    )

    record = HistoryRecord(
        id=record_id,
        task_type=task_type,
        provider=provider,
        input_data=input_data,
        result_data=str(result_data),
    )
    db.add(record)
    db.commit()

    return f"{record_id}.json"  # 프론트엔드 호환용 리턴
  except Exception as e:
    db.rollback()
    print(f"⚠️ DB 히스토리 저장 실패: {e}")
    raise e
  finally:
    db.close()


def get_all_file_histories():
  """DB에서 모든 기록을 최신순으로 읽어옵니다."""
  db = SessionLocal()
  try:
    records = (
        db.query(HistoryRecord)
        .order_by(HistoryRecord.created_at.desc())
        .all()
    )
    history_list = []
    for r in records:
      history_list.append({
          "id": f"{r.id}.json",
          "task_type": r.task_type,
          "provider": r.provider,
          "input_data": r.input_data,
          "result_data": r.result_data,
          "created_at": (
              r.created_at.strftime("%Y-%m-%d %H:%M:%S")
              if r.created_at
              else ""
          ),
      })
    return history_list
  finally:
    db.close()


def delete_file_history(file_id: str) -> bool:
  """지정된 ID의 기록을 DB에서 삭제합니다."""
  db = SessionLocal()
  try:
    clean_id = file_id.replace(".json", "")
    record = (
        db.query(HistoryRecord).filter(HistoryRecord.id == clean_id).first()
    )
    if record:
      db.delete(record)
      db.commit()
      return True
    return False
  except Exception as e:
    db.rollback()
    print(f"⚠️ DB 히스토리 삭제 실패: {e}")
    return False
  finally:
    db.close()