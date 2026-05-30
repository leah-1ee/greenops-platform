import requests
from typing import Optional

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


# AI 서버 기본 설정
AI_SERVICE_URL = "http://localhost:8001"
AI_TIMEOUT_SEC = 5


# ─── 헬퍼 함수 ──────────────────────────────────────────────────────────────

def _call_ai(endpoint: str, params: dict = None) -> dict:
    url = f"{AI_SERVICE_URL}{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=AI_TIMEOUT_SEC)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"AI 서버 호출 실패 ({url}): {e}")
        raise


# ─── 실시간 탄소 강도 조회 ──────────────────────────────────────────────────

def get_current_intensity(zone: str) -> float:
    logger.debug(f"실시간 탄소 강도 조회: zone={zone}")
    
    data = _call_ai("/intensity/current", params={"zone": zone})
    
    # 응답 형식 검증
    # 예: {"zone": "KR", "carbonIntensity": 409.5, "datetime": "...", "isEstimated": true}
    if "carbonIntensity" not in data:
        raise ValueError(f"예상치 못한 AI 응답 형식: {data}")
    
    intensity = float(data["carbonIntensity"])
    logger.info(f"AI 실시간 탄소 강도: {zone} = {intensity} gCO₂/kWh")
    
    return intensity


# ─── 최적 시점 추천 ────────────────────────────────────────────────────────

def get_recommendation(hours: int, zones: list[str]) -> dict:
    logger.debug(f"AI 추천 요청: hours={hours}, zones={zones}")
    
    # zones는 &zones=KR&zones=JP-TK 형식 (콤마 아님)
    # requests가 list를 자동으로 이렇게 변환해줌
    params = {
        "hours": hours,
        "zones": zones,
    }
    
    data = _call_ai("/recommendation", params=params)
    logger.info(f"AI 추천 받음: best_zone={data.get('best_zone')}, opt_time={data.get('opt_time')}")
    
    return data


# ─── 헬스체크 ──────────────────────────────────────────────────────────────

def is_ai_alive() -> bool:
    try:
        response = requests.get(
            f"{AI_SERVICE_URL}/health",
            timeout=2,
        )
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"AI 헬스체크 실패: {e}")
        return False