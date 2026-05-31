from pydantic import BaseModel, Field


class RegionDetail(BaseModel):
    """ 리전 상세 정보 """
    name: str = Field(..., description="리전 이름 (한글)")
    pue: float = Field(..., description="데이터센터 PUE")
    sdk_location: str = Field(..., description="Carbon Aware SDK 위치 코드")
    carbon_intensity: int = Field(..., description="탄소 강도 (gCO₂/kWh)")


class RegionListResponse(BaseModel):
    """ 전체 리전 목록 응답 """
    regions: dict[str, RegionDetail] = Field(..., description="리전 코드 → 상세 정보")


class RegionDetailResponse(RegionDetail):
    """ 단일 리전 상세 응답 """
    region_code: str = Field(..., description="AWS 리전 코드")
