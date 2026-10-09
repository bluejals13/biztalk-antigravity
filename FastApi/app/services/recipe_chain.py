# app/services/recipe_chain.py
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_llm

def generate_recipe(ingredients: str, provider: str = "groq", length_level: int = 2) -> str:
    """재료를 입력받아 레시피를 문자열로 반환합니다."""
    
    length_guides = {
        1: "핵심만 아주 짧고 간결하게 요약하여 답변하세요.",
        2: "불필요한 내용은 빼고 평균보다 살짝 짧고 간결하게 답변하세요.",
        3: "표준적이고 균형 잡힌 분량으로 답변하세요.",
        4: "세부적인 내용과 배경을 포함하여 상세히 답변하세요.",
        5: "매우 풍부하고 깊이 있는 정보를 바탕으로 최대한 길고 상세히 답변하세요."
    }
    guide = length_guides.get(length_level, length_guides[2])

    llm = get_llm(provider=provider) # provider 전달
    
    # 💡 프롬프트 템플릿에 guide 제약조건 포함
    prompt = PromptTemplate.from_template(
        "다음 재료들로 만들 수 있는 요리를 추천하고 레시피를 알려주세요.\n"
        "재료: {ingredients}\n"
        "[답변 스타일 제약] {guide}"
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"ingredients": ingredients, "guide": guide})