from fastapi import APIRouter, Query, HTTPException
from typing import List
from llm.report_generator import generate_carbon_report

router = APIRouter()

@router.get("")
def recommendation_report(
    hours: int = 3,
    zones: List[str] = Query(["KR", "JP-TK", "US-MIDA-PJM"])
):
    """
    각 리전별 탄소 집약도 예측 통계치를 기반으로
    가장 효율적인 시간대 및 리전을 추천해주는 한글 자연어 리포트를 생성하여 반환합니다.
    """
    try:
        report_text = generate_carbon_report(work_hours=hours, zones=zones)
        return {"report": report_text}
    except KeyError as ke:
        # API 토큰 누락 시 에러 상태코드 반환
        raise HTTPException(
            status_code=500,
            detail=f"서버 환경설정 에러: {str(ke)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"리포트 생성 오류: {str(e)}"
        )
