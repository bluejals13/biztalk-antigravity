from pydantic import BaseModel, Field

class ConvertRequest(BaseModel):
    text: str = Field(..., description="변환할 원문 텍스트", min_length=1)
    target_audience: str = Field(..., description="수신 대상 (boss | colleague | client | team)")

class ConvertResponse(BaseModel):
    converted_text: str = Field(..., description="변환된 텍스트")
    target_audience: str = Field(..., description="수신 대상 코드")
    original_text: str = Field(..., description="변환 전 원문 텍스트")
