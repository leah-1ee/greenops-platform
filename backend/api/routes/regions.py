from fastapi import APIRouter

from core.regions import REGION_DATA, get_region
from schemas.regions import RegionListResponse, RegionDetailResponse
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("")
def get_all_regions():
    """ 지원하는 모든 리전 목록 반환 """
    logger.debug("전체 리전 목록 조회")
    return {"regions": REGION_DATA}


@router.get("/{region_code}")
def get_region_detail(region_code: str):
    """
    특정 리전의 상세 정보 조회

    예: GET /api/v1/regions/ap-northeast-2
    """
    logger.debug(f"리전 조회: {region_code}")
    try:
        region = get_region(region_code)
        return {
            "region_code": region_code,
            **region,
        }
    except ValueError as e:
        from fastapi import HTTPException
        logger.warning(f"지원하지 않는 리전: {region_code}")
        raise HTTPException(status_code=404, detail=str(e))