from fastapi import APIRouter
from analysis.region_scorer import get_best_region

router = APIRouter()

@router.get("")
def recommendation(hours: int = 3):
    zones = ["KR", "JP-TK", "US-MIDA-PJM"]
    result = get_best_region(hours, zones)
    return result or {"error": "데이터 없음"}
