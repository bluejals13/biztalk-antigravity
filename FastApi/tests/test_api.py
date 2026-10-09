# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.api.routes.generate_recipe")
def test_api_get_recipe(mock_generate):
    mock_generate.return_value = "맛있는 볶음밥 레시피"
    
    response = client.post("/api/v1/recipe", json={"ingredients": "계란, 밥"})
    
    assert response.status_code == 200
    assert response.json() == {"result": "맛있는 볶음밥 레시피"}

def test_api_get_recipe_validation_error():
    # 빈 값을 보내면 Pydantic이 422 Unprocessable Entity 에러를 내야 합니다.
    response = client.post("/api/v1/recipe", json={"ingredients": ""})
    assert response.status_code == 422

@patch("app.api.routes.generate_tour_info")
def test_api_get_tour(mock_tour):
    mock_tour.return_value = {"landmark": "콜로세움", "details": "상세 설명"}
    
    response = client.post("/api/v1/tour", json={"location": "로마"})
    
    assert response.status_code == 200
    assert response.json()["landmark"] == "콜로세움"

@patch("app.api.routes.extract_news_keywords")
def test_api_extract_news_keywords_error_handling(mock_extract):
    # 서비스 계층에서 예외가 발생했을 때 502 에러로 잘 감싸서 반환하는지 검증
    mock_extract.side_effect = Exception("API Rate Limit Exceeded")
    
    response = client.post("/api/v1/news", json={"news_text": "아주 긴 뉴스 기사 본문 내용입니다..."})
    
    assert response.status_code == 502
    assert "API Rate Limit Exceeded" in response.json()["detail"]