from fastapi import APIRouter
from carbon_aware.realtime_client import get_current_intensity
router = APIRouter()

@router.get("/current")
def current_intensity(zone: str = "KR"):
    result = get_current_intensity(zone)
    return result or {"error": "데이터 없음"}
