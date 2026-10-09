# app/services/news_chain.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_llm

def extract_news_keywords(news_text: str, provider: str = "groq", length_level: int = 2) -> str:
    """뉴스 본문을 입력받아 키워드 및 요약을 반환합니다."""
    
    length_guides = {
        1: "핵심 키워드만 아주 짧고 간결하게 요약하세요.",
        2: "불필요한 내용은 빼고 평균보다 살짝 짧고 간결하게 요약하세요.",
        3: "표준적이고 균형 잡힌 분량으로 요약하세요.",
        4: "세부적인 내용과 배경을 포함하여 상세히 요약하세요.",
        5: "매우 풍부하고 깊이 있는 정보를 바탕으로 최대한 길고 상세히 요약하세요."
    }
    guide = length_guides.get(length_level, length_guides[2])

    llm = get_llm(provider=provider)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"당신은 전문 뉴스 분석가입니다. 주어진 뉴스 본문에서 핵심 키워드와 요약을 작성해주세요.\n[답변 스타일 제약] {guide}"),
        ("user", "{news_text}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"news_text": news_text})