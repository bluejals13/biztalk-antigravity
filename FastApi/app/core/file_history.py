# core/file_history.py
import os
import json
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 내의 history_records 폴더 지정
HISTORY_DIR = Path("history_records")
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

MAX_HISTORY_COUNT = 20  # 최대 유지 개수

def save_file_history(task_type: str, provider: str, input_data: str, result_data: str) -> str:
    """결과를 지정된 폴더에 JSON 파일로 저장하며, 최대 20개를 초과하면 가장 오래된 기록을 삭제합니다."""
    
    # 1. 현재 저장된 히스토리 파일들을 이름순(시간순)으로 정렬하여 가져옴
    files = sorted(HISTORY_DIR.glob("*.json"))
    
    # 2. 개수가 20개 이상이면, 새로운 파일이 들어올 자리를 만들기 위해 가장 오래된 파일 삭제
    while len(files) >= MAX_HISTORY_COUNT:
        oldest_file = files.pop(0)  # 가장 오래된 파일 선택
        try:
            if oldest_file.exists():
                oldest_file.unlink()  # 파일 삭제
        except Exception as e:
            print(f"⚠️ 오래된 히스토리 파일 삭제 실패: {e}")

    # 3. 새로운 히스토리 파일 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]
    filename = f"{timestamp}_{task_type}.json"
    file_path = HISTORY_DIR / filename
    
    record = {
        "id": filename,  # 파일명을 고유 ID로 사용
        "task_type": task_type,
        "provider": provider,
        "input_data": input_data,
        "result_data": str(result_data),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=4)
        
    return filename

def get_all_file_histories():
    """history_records 폴더 내의 모든 기록을 최신순으로 읽어옵니다."""
    records = []
    if not HISTORY_DIR.exists():
        return records
        
    for file_path in sorted(HISTORY_DIR.glob("*.json"), reverse=True):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                records.append(json.load(f))
        except Exception:
            continue
    return records

def delete_file_history(file_id: str) -> bool:
    """지정된 파일 ID(파일명)의 기록 파일을 삭제합니다."""
    file_path = HISTORY_DIR / file_id
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
        return True
    return False
