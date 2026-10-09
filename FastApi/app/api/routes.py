# app/api/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .services.recipe_chain import generate_recipe
from .services.tour_chain import generate_tour_info
from .services.news_chain import extract_news_keywords
from .services.search_agent import run_search_agent
from ..core.file_history import (
    save_file_history, 
    get_all_file_histories, 
    delete_file_history
)

router = APIRouter()

# --- Pydantic 데이터 검증 모델 (length_level 기본값 2 설정) ---
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
        result = extract_news_keywords(req.news_text, req.provider, req.length_level)
        save_file_history("news", req.provider, req.news_text, result)
        return {"keywords": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"뉴스 키워드 추출 오류: {str(e)}")

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

