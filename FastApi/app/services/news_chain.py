# app/services/news_chain.py
from langchain_core.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_llm

def extract_news_keywords(news_text: str, provider: str = "groq") -> str:
    """뉴스 텍스트를 입력받아 핵심 키워드를 반환합니다."""
    llm = get_llm(provider=provider, temperature=0.0) # provider 및 temperature 전달
    
    examples = [
        {
            "news": "삼성전자가 내년 초에 자체적으로 개발한 인공지능(AI) 가속기를 처음으로 출시할 예정이다.",
            "keywords": "삼성전자, 인공지능, 출시"
        },
        {
            "news": "세계보건기구(WHO)는 최근 새로운 건강 위기에 대응하기 위해 국제 협력의 중요성을 강조했다.",
            "keywords": "세계보건기구, 건강위기, 국제협력"
        },
        {
            "news": "한국은행이 오늘 기준금리를 연 3.5%로 동결했습니다.",
            "keywords": "한국은행, 기준금리, 동결"
        }
    ]

    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{news}"),
        ("ai", "키워드: {keywords}")
    ])

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples
    )

    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "뉴스 키워드 추출 전문가입니다. 기사 내용을 읽고 가장 핵심적인 키워드 3개를 추출하세요."),
        few_shot_prompt,
        ("human", "{input}")
    ])

    chain = final_prompt | llm | StrOutputParser()
    return chain.invoke({"input": news_text})