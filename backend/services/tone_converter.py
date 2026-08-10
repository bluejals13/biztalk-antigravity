import os
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
from langchain_core.messages import SystemMessage, HumanMessage
from backend.prompts.templates import PROMPTS, DEFAULT_PROMPT

# 환경변수 로드 (.env)
load_dotenv()

class ToneConverterService:
    def __init__(self):
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise ValueError("UPSTAGE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        
        # Upstage Solar-Pro3 모델 초기화
        self.llm = ChatUpstage(
            api_key=api_key,
            model="solar-pro3",
            temperature=0.3,
        )

    async def convert(self, text: str, target_audience: str) -> str:
        """
        입력된 text와 target_audience에 맞춰 말투를 변환합니다.
        """
        system_instruction = PROMPTS.get(target_audience, DEFAULT_PROMPT)
        
        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=f"다음 원문을 변환해주세요:\n\n{text}")
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            converted_content = response.content.strip()
            return converted_content
        except Exception as e:
            # 동기 호출 폴백 또는 에러 전파
            try:
                response = self.llm.invoke(messages)
                return response.content.strip()
            except Exception as ex:
                raise RuntimeError(f"Solar-Pro3 LLM 변환 중 오류가 발생했습니다: {str(ex)}")

tone_converter_service = ToneConverterService()
