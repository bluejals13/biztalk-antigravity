# app/services/tour_chain.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import get_llm

def generate_tour_info(location: str, provider: str = "groq", length_level: int = 2) -> dict:
    """도시를 입력받아 랜드마크와 상세 정보를 딕셔너리로 반환합니다."""
    
    length_guides = {
        1: "핵심만 아주 짧고 간결하게 요약하여 답변하세요.",
        2: "불필요한 내용은 빼고 평균보다 살짝 짧고 간결하게 답변하세요.",
        3: "표준적이고 균형 잡힌 분량으로 답변하세요.",
        4: "세부적인 내용과 배경을 포함하여 상세히 답변하세요.",
        5: "매우 풍부하고 깊이 있는 정보를 바탕으로 최대한 길고 상세히 답변하세요."
    }
    guide = length_guides.get(length_level, length_guides[2])

    llm = get_llm(provider=provider) # provider 전달
    
    # 1단계: 명소 추천
    prompt1 = ChatPromptTemplate.from_messages([
        ("system", "당신은 전문 여행 가이드입니다. 사용자가 입력한 도시나 국가를 대표하는 가장 유명한 명소 1곳의 '이름'만 짧게 대답하세요."),
        ("user", "{location}")
    ])
    chain1 = prompt1 | llm | StrOutputParser()

    # 2단계: 상세 정보 생성 (💡 guide 제약조건 추가)
    prompt2 = ChatPromptTemplate.from_messages([
        ("system", f"당신은 친절한 여행 가이드입니다. 주어진 명소에 대해 역사, 특징, 방문 팁을 각각 번호 매겨 설명해주세요.\n[답변 스타일 제약] {guide}"),
        ("user", "{landmark}에 대한 상세 정보를 알려주세요.")
    ])
    chain2 = prompt2 | llm | StrOutputParser()

    # 다중 체인 연결
    multi_chain = (
        {"landmark": chain1} 
        | RunnablePassthrough.assign(details=chain2)
    )
    
    return multi_chain.invoke({"location": location})