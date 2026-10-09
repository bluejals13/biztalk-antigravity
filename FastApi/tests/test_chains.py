# tests/test_chains.py
import pytest
from unittest.mock import patch
from langchain_core.messages import AIMessage

from app.services.recipe_chain import generate_recipe
from app.services.tour_chain import generate_tour_info
from app.services.news_chain import extract_news_keywords

# ChatOpenAI의 내부 invoke 메서드를 가로챕니다.
@patch("app.core.config.ChatOpenAI.invoke")
def test_recipe_chain(mock_invoke):
    # LLM이 반환할 가짜 응답 설정
    mock_invoke.return_value = AIMessage(content="추천 요리: 김치볶음밥\n레시피: ...")
    
    result = generate_recipe("계란, 밥, 김치")
    
    assert "김치볶음밥" in result
    mock_invoke.assert_called_once() # LLM이 딱 한 번 호출되었는지 검증

@patch("app.core.config.ChatOpenAI.invoke")
def test_tour_chain(mock_invoke):
    # 다중 체인이므로 LLM이 2번 호출됩니다. side_effect로 순차적 응답을 설정합니다.
    mock_invoke.side_effect = [
        AIMessage(content="콜로세움"),               # 1단계 명소 추천 응답
        AIMessage(content="1. 역사: 로마 제국...")   # 2단계 상세 정보 응답
    ]
    
    result = generate_tour_info("로마")
    
    assert result["landmark"] == "콜로세움"
    assert "역사: 로마 제국" in result["details"]
    assert mock_invoke.call_count == 2 # 2단계 체인이므로 2번 호출되었는지 검증

@patch("app.core.config.ChatOpenAI.invoke")
def test_news_chain(mock_invoke):
    mock_invoke.return_value = AIMessage(content="키워드: 제미나이, 구글AI, 개발자")
    
    result = extract_news_keywords("제미나이 2.0 플래시는 현재 구글 AI 스튜디오...")
    
    assert "제미나이" in result
    assert "구글AI" in result