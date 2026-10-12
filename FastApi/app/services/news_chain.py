# app/services/news_chain.py
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_llm

# ==========================================
# 1. 다목적 분석용 Pydantic 스키마 정의
# ==========================================
class DocumentAnalysis(BaseModel):
    title: str = Field(description="문서의 내용을 대표하는 핵심 제목")
    summary: str = Field(description="지정된 분량 가이드에 맞춘 전체 내용 요약")
    keywords: List[str] = Field(description="검색 및 태그용 핵심 키워드 3~5개")
    entities: List[str] = Field(description="문서에 등장하는 주요 인물, 기업, 기관, 장소 리스트")
    takeaways: List[str] = Field(description="이 문서에서 얻을 수 있는 핵심 시사점이나 결론 (3줄 이내)")
    
    # 💡 새로 추가된 필드 (선택적 추출)
    api_json_spec: Optional[str] = Field(
        default=None, 
        description="[Level 4~5 전용] 문서에 API 명세, JSON 구조, 또는 기술적 스펙이 있다면 마크다운 형태로 추출. 없거나 레벨이 낮으면 null"
    )

# ==========================================
# 2. 문서 가공 체인 함수
# ==========================================
def extract_document_insights(doc_text: str, provider: str = "groq", length_level: int = 2) -> dict:
    
    # 💡 4~5 레벨에서만 api_json_spec 필드를 활성화하도록 프롬프트 지시어 수정
    length_guides = {
        1: "요약을 핵심 키워드 중심의 1~2문장으로 아주 짧게 작성하세요. (api_json_spec 필드는 무조건 null로 비워두세요)",
        2: "요약을 불필요한 수식어를 뺀 3~4문장으로 간결하게 작성하세요. (api_json_spec 필드는 무조건 null로 비워두세요)",
        3: "요약을 표준적이고 균형 잡힌 1문단(5~6문장)으로 작성하세요. (api_json_spec 필드는 무조건 null로 비워두세요)",
        4: "요약을 세부 배경과 논리를 포함하여 2문단 이상으로 상세히 작성하세요. 만약 문서 내용 중에 개발/기술/API JSON 명세가 있다면 `api_json_spec` 필드에 마크다운 코드 블록 형태로 반드시 추출하세요.",
        5: "요약을 문서의 주요 논점을 포함하여 최대한 풍부하고 깊이 있게 작성하세요. 문서 내에 기술 데이터, API 스펙, JSON 명세 등이 하나라도 있다면 `api_json_spec` 필드에 완벽한 마크다운 코드 블록 형태로 추출하세요."
    }
    guide = length_guides.get(length_level, length_guides[2])

    llm = get_llm(provider=provider)
    structured_llm = llm.with_structured_output(DocumentAnalysis)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 전문 문서 분석가(Document Analyst)입니다. 
        주어진 긴 글(뉴스, PDF 추출 텍스트 등)을 분석하여 요청된 구조에 맞게 데이터를 추출하세요.
        
        [요약 지침 및 특수 요구사항]
        {guide}"""),
        ("user", "다음 문서를 분석해 주세요:\n\n{doc_text}")
    ])
    
    chain = prompt | structured_llm
    result: DocumentAnalysis = chain.invoke({
        "guide": guide,
        "doc_text": doc_text
    })
    
    return result.model_dump()
