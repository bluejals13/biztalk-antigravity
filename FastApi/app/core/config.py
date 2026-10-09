# app/core/.config.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_upstage import ChatUpstage 

load_dotenv()

def get_llm(provider: str = "groq", temperature: float = 0.3):
    """provider 이름에 따라 알맞은 LLM 인스턴스를 반환합니다."""
    
    if provider == "openai":
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), 
            model="gpt-4o-mini", 
            temperature=temperature
        )
        
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GOOGLE_API_KEY"), 
            model="gemini-3.1-flash-lite",  # <--- 노트북에서 검증된 최신 모델 적용
            temperature=temperature
        )
        
    elif provider == "upstage": 
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise RuntimeError("UPSTAGE_API_KEY가 설정되지 않았습니다.")
        return ChatUpstage(
            api_key=api_key, 
            model="solar-1-mini-chat", 
            temperature=temperature
        )
        
    else: # groq (노트북에서 검증된 모델 적용)
        return ChatOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            model="openai/gpt-oss-120b", 
            temperature=temperature
        )