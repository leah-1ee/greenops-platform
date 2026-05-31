from pydantic import BaseModel, Field


class CarbonResult(BaseModel):
    """ 단일 CO₂ 계산 결과 """
    cpu_percent: float = Field(..., description="CPU 사용률 (%)")
    memory_gb: float = Field(..., description="메모리 사용량 (GB)")
    instance_type: str = Field(..., description="인스턴스 타입 (예: t3.medium)")
    region_code: str = Field(..., description="AWS 리전 코드")
    duration_sec: int = Field(..., description="측정 구간 (초)")
    region_name: str = Field(..., description="리전 이름 (한글)")
    tdp_watt: int = Field(..., description="인스턴스 TDP (W)")
    pue: float = Field(..., description="데이터센터 PUE")
    carbon_intensity: float = Field(..., description="탄소 강도 (gCO₂/kWh)")
    intensity_source: str = Field(..., description="탄소 강도 출처 (ai / fallback)")
    power_watt: float = Field(..., description="실제 소비 전력 (W)")
    energy_kwh: float = Field(..., description="전력량 (kWh)")
    co2_grams: float = Field(..., description="CO₂ 배출량 (g)")


class NodeCarbonResponse(CarbonResult):
    """ 노드 단위 CO₂ 응답 """
    timestamp: str = Field(..., description="측정 시각 (ISO 8601)")
    source: str = Field(..., description="데이터 소스 (mock / prometheus)")


class PodCarbonItem(CarbonResult):
    """ 파드별 CO₂ 결과 (목록 내 개별 항목) """
    pod_name: str = Field(..., description="파드 이름")
    share_percent: float = Field(..., description="노드 대비 CPU 점유율 (%)")


class PodCarbonResponse(BaseModel):
    """ 파드별 CO₂ 응답 """
    timestamp: str = Field(..., description="측정 시각 (ISO 8601)")
    source: str = Field(..., description="데이터 소스 (mock / prometheus)")
    pods: list[PodCarbonItem] = Field(..., description="파드별 CO₂ 목록")
