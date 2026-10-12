# app/core/config.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_upstage import ChatUpstage 
# 💡 사내망(Ollama) 연동을 위한 모듈 추가
from langchain_ollama import ChatOllama

load_dotenv()

# 💡 사내(로컬) Ollama 서버 주소 고정 설정
OLLAMA_BASE_URL = "http://192.168.45.218:11434"

def get_llm(provider: str = "groq", temperature: float = 0.3):
    """provider 이름에 따라 알맞은 LLM 인스턴스를 반환합니다."""
    
    # ==========================================
    # 1. 기존 클라우드 모델 (완벽 유지)
    # ==========================================
    if provider == "openai":
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), 
            model="gpt-4o-mini", 
            temperature=temperature
        )
        
    elif provider == "groq":
         return ChatOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            model="openai/gpt-oss-120b", 
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
        
    # ==========================================
    # 2. 새로 추가된 사내망 로컬 모델 (Ollama)
    # ==========================================
    elif provider == "ollama_qwen3":
        return ChatOllama(
            model="qwen3:8b-q4_K_M", 
            base_url=OLLAMA_BASE_URL, 
            temperature=temperature
        )
        
    elif provider == "ollama_qwen25":
        return ChatOllama(
            model="qwen2.5:0.5b", 
            base_url=OLLAMA_BASE_URL, 
            temperature=temperature
        )
        
    elif provider == "ollama_deepseek":
        return ChatOllama(
            model="deepseek-r1:8b-llama-distill-q4_K_M", 
            base_url=OLLAMA_BASE_URL, 
            temperature=temperature
        )

    # ==========================================
    # 3. 기본값 (groq - 기존 로직 유지)
    # ==========================================
    else: 
        return ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GOOGLE_API_KEY"), 
            model="gemini-3.1-flash-lite",  # 노트북에서 검증된 최신 모델 적용
            temperature=temperature
        )