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
    
    # 🌟 [수정 포인트] Azure 리전 코드를 AI 서버가 인식하는 국가 코드로 매핑
    # 백엔드가 넘겨준 'koreacentral'을 AI 서버용 'KR'로 변환합니다.
    zone_to_country = {
        "koreacentral": "KR",
        "japaneast": "JP",
        "eastus": "US"
    }
    
    # 매핑 테이블에 존재하면 해당 국가 코드를 쓰고, 없으면 기존 값 그대로 사용
    ai_zone = zone_to_country.get(zone, zone)
    
    # 파라미터에 기존 zone 대신 국가 코드가 담긴 ai_zone을 전달합니다.
    data = _call_ai("/intensity/current", params={"zone": ai_zone})
    
    # 응답 형식 검증
    # 예: {"zone": "KR", "carbonIntensity": 328, "datetime": "...", "isEstimated": true}
    if "carbonIntensity" not in data:
        raise ValueError(f"예상치 못한 AI 응답 형식: {data}")
    
    intensity = float(data["carbonIntensity"])
    logger.info(f"AI 실시간 탄소 강도: {ai_zone} = {intensity} gCO₂/kWh")
    
    return intensity


# ─── 최적 시점 추천 ────────────────────────────────────────────────────────

def get_recommendation(hours: int, zones: list[str]) -> dict:
    logger.debug(f"AI 추천 요청: hours={hours}, zones={zones}")
    
    # 🌟 [수정 포인트] 추천 기능에서도 Azure 리전을 국가 코드로 채가도록 변환
    zone_to_country = {
        "koreacentral": "KR",
        "japaneast": "JP",
        "eastus": "US"
    }
    ai_zones = [zone_to_country.get(z, z) for z in zones]
    
    params = {
        "hours": hours,
        "zones": ai_zones,  # 변환된 국가 코드 리스트 전달
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