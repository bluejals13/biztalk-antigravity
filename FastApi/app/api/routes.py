# app/api/routes.py
import io
import zipfile
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HistoryRecord
from app.services.recipe_chain import generate_recipe
from app.services.tour_chain import generate_tour_info
from app.services.news_chain import extract_document_insights
from app.services.search_agent import run_search_agent
from app.core.file_history import (
    save_file_history, 
    get_all_file_histories, 
    delete_file_history
)

router = APIRouter()

# --- Pydantic 데이터 검증 모델 ---
class RecipeRequest(BaseModel):
    ingredients: str = Field(..., min_length=1, examples=["계란, 밥, 김치"])
    provider: str = Field(default="upstage")
    length_level: int = Field(default=2, ge=1, le=5)

class TourRequest(BaseModel):
    location: str = Field(..., min_length=1, examples=["로마"])
    provider: str = Field(default="upstage")
    length_level: int = Field(default=2, ge=1, le=5)

class NewsRequest(BaseModel):
    news_text: str = Field(..., min_length=10, max_length=3000)
    provider: str = Field(default="upstage")
    length_level: int = Field(default=2, ge=1, le=5)

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, examples=["오늘 서울 날씨 어때?"])
    provider: str = Field(default="openai")
    length_level: int = Field(default=2, ge=1, le=5)


# --- AI 서비스 엔드포인트 ---

@router.post("/recipe")
def api_get_recipe(req: RecipeRequest):
    try:
        result = generate_recipe(req.ingredients, req.provider, req.length_level)
        save_file_history("recipe", req.provider, req.ingredients, result)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 요리사 체인 오류: {str(e)}")

@router.post("/tour")
def api_get_tour(req: TourRequest):
    try:
        result = generate_tour_info(req.location, req.provider, req.length_level)
        save_file_history("tour", req.provider, req.location, str(result))
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"여행지 다중 체인 오류: {str(e)}")

@router.post("/news")
def api_extract_keywords(req: NewsRequest):
  try:
    # 딕셔너리 형태로 결과 반환됨 (title, summary, keywords, entities, takeaways)
    result = extract_document_insights(
        req.news_text, req.provider, req.length_level
    )
    # 히스토리에는 전체 결과를 보기 좋게 문자열(또는 JSON)로 저장
    save_file_history("news", req.provider, req.news_text, str(result))
    return result
  except Exception as e:
    raise HTTPException(
        status_code=502, detail=f"문서 분석 및 키워드 추출 오류: {str(e)}"
    )

@router.post("/search")
def api_search(req: SearchRequest):
    try:
        result = run_search_agent(req.query, req.provider, req.length_level)
        save_file_history("search", req.provider, req.query, result)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"검색 에이전트 오류: {str(e)}")


# --- 파일 히스토리 관리 엔드포인트 ---

@router.get("/history")
def api_get_history():
    try:
        items = get_all_file_histories()
        return {"history": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 오류: {str(e)}")

@router.delete("/history/{file_id}")
def api_delete_history(file_id: str):
    success = delete_file_history(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="해당 기록 파일을 찾을 수 없습니다.")
    return {"message": f"기록 파일 {file_id}이(가) 삭제되었습니다."}

@router.get("/history/export/zip")
def export_history_zip(db: Session = Depends(get_db)):
    """모든 히스토리를 개별 .md 파일과 index.csv가 포함된 .zip 파일로 내보냅니다."""
    records = (
        db.query(HistoryRecord)
        .order_by(HistoryRecord.created_at.desc())
        .all()
    )

    zip_buffer = io.BytesIO()
    index_data = []

    with zipfile.ZipFile(
        zip_buffer, "w", zipfile.ZIP_DEFLATED
    ) as zip_file:
        for r in records:
            clean_id = r.id.replace(".json", "")
            file_name = f"{clean_id}_{r.task_type}.md"

            md_content = f"""# [AI Backend Lab Record]

- **작업 유형:** {r.task_type.upper()}
- **사용 모델:** {r.provider}
- **생성 시간:** {r.created_at}

## [전체 입력 내용]
{r.input_data}

## [상세 전체 대답]
{r.result_data}
"""
            zip_file.writestr(f"history_files/{file_name}", md_content)

            index_data.append({
                "id": r.id,
                "task_type": r.task_type,
                "provider": r.provider,
                "file_name": file_name,
                "created_at": (
                    r.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if r.created_at
                    else ""
                ),
            })

        df = pd.DataFrame(index_data)
        csv_bytes = (
            df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            if not df.empty
            else b"id,task_type,provider,file_name,created_at\n"
        )
        zip_file.writestr("index.csv", csv_bytes)

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                "attachment; filename=my_history_export.zip"
            )
        },
    )