# app/services/search_agent.py
from langchain_tavily import TavilySearch
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_llm

def run_search_agent(query: str, provider: str = "openai", length_level: int = 2) -> str:
    tools = [TavilySearch(max_results=3)]
    
    length_guides = {
        1: "핵심만 아주 짧고 간결하게 요약하여 답변하세요.",
        2: "불필요한 내용은 빼고 평균보다 살짝 짧고 간결하게 답변하세요.",
        3: "표준적이고 균형 잡힌 분량으로 답변하세요.",
        4: "세부적인 내용과 배경을 포함하여 상세히 답변하세요.",
        5: "매우 풍부하고 깊이 있는 정보를 바탕으로 최대한 길고 상세히 답변하세요."
    }
    guide = length_guides.get(length_level, length_guides[2])

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"당신은 최신 정보를 검색하여 답변하는 AI 어시스턴트입니다. 검색 내용을 바탕으로 답변하며 반드시 출처를 언급하세요. [답변 스타일 제약] {guide}"),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    llm = get_llm(provider=provider)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    result = agent_executor.invoke({"input": query})
    output = result.get("output", "")
    
    # 만약 결과가 리스트나 딕셔너리 형태라면 문자열로 안전하게 변환
    if isinstance(output, list):
        text_parts = []
        for item in output:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
            else:
                text_parts.append(str(item))
        return "\n".join(text_parts)
    
    return str(output)