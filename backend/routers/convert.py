from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import ConvertRequest, ConvertResponse
from backend.services.tone_converter import tone_converter_service

router = APIRouter()

@router.post("/convert", response_model=ConvertResponse, summary="업무 말투 변환 API")
async def convert_tone(payload: ConvertRequest):
    """
    원문 텍스트(text)와 수신 대상(target_audience: boss | colleague | client | team)을 수신하여
    Upstage Solar-Pro3 모델을 활용해 적절한 비즈니스 말투로 변환합니다.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="text 필드는 필수입니다."
        )
    
    valid_targets = {"boss", "colleague", "client", "team"}
    if payload.target_audience not in valid_targets:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"target_audience는 다음 중 하나여야 합니다: {', '.join(valid_targets)}"
        )

    try:
        converted_text = await tone_converter_service.convert(
            text=payload.text,
            target_audience=payload.target_audience
        )
        return ConvertResponse(
            converted_text=converted_text,
            target_audience=payload.target_audience,
            original_text=payload.text
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM API 호출 중 오류가 발생했습니다: {str(e)}"
        )
