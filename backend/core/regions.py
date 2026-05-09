"""
리전별 탄소 계수 및 인스턴스 TDP 데이터

데이터 출처:
- carbon_intensity: IEA (국제에너지기구) 2024 국가별 평균 탄소강도
- pue: AWS Sustainability Report 2024 / Uptime Institute 글로벌 평균
- sdk_location: Microsoft Carbon Aware SDK location identifier
- TDP: AWS EC2 인스턴스 스펙 + Cloud Carbon Footprint 프로젝트 데이터
"""


# ─── 리전별 탄소 계수 데이터 ────────────────────────────────────────────────
REGION_DATA = {
    "ap-northeast-2": {
        "name": "서울",
        "pue": 1.15,
        "sdk_location": "KR",
        "carbon_intensity": 415,  # gCO₂/kWh, IEA 2024 한국 평균
    },
    "ap-northeast-1": {
        "name": "도쿄",
        "pue": 1.20,
        "sdk_location": "JP",
        "carbon_intensity": 506,  # gCO₂/kWh, IEA 2024 일본 평균
    },
    "us-east-1": {
        "name": "버지니아",
        "pue": 1.18,
        "sdk_location": "US-MIDA-PJM",
        "carbon_intensity": 391,  # gCO₂/kWh, EIA 2024 PJM Interconnection 평균
    },
}


# ─── 인스턴스 타입별 TDP (Thermal Design Power) ─────────────────────────────
INSTANCE_TDP = {
    # T3 시리즈 (범용 - 버스트 가능)
    "t3.nano":    5,
    "t3.micro":   10,
    "t3.small":   15,
    "t3.medium":  15,
    "t3.large":   20,
    "t3.xlarge":  40,
    "t3.2xlarge": 80,

    # M5 시리즈 (범용)
    "m5.large":    40,
    "m5.xlarge":   80,
    "m5.2xlarge":  160,
    "m5.4xlarge":  320,

    # C5 시리즈 (컴퓨팅 최적화)
    "c5.large":    35,
    "c5.xlarge":   70,
    "c5.2xlarge":  140,
    "c5.4xlarge":  280,

    # R5 시리즈 (메모리 최적화)
    "r5.large":    45,
    "r5.xlarge":   90,
    "r5.2xlarge":  180,

    # 기본값 (알 수 없는 인스턴스 타입)
    "default": 20,
}



def get_region(region_code: str) -> dict:
    """
    리전 코드로 탄소 계수 정보 조회

    Args:
        region_code: AWS 리전 코드 (예: "ap-northeast-2")

    Returns:
        리전 정보 딕셔너리 (name, pue, sdk_location, carbon_intensity)

    Raises:
        ValueError: 지원하지 않는 리전 코드인 경우
    """
    if region_code not in REGION_DATA:
        supported = ", ".join(REGION_DATA.keys())
        raise ValueError(
            f"NO supported regions: {region_code} "
            f"(supported regions: {supported})"
        )
    return REGION_DATA[region_code]


def get_tdp(instance_type: str) -> int:
    """
    인스턴스 타입으로 TDP 조회 (없으면 기본값 반환)

    Args:
        instance_type: AWS 인스턴스 타입 (예: "t3.medium")

    Returns:
        TDP 값 (W)
    """
    return INSTANCE_TDP.get(instance_type, INSTANCE_TDP["default"])


def get_supported_regions() -> list[str]:
    """지원하는 리전 코드 목록 반환"""
    return list(REGION_DATA.keys())


def get_sdk_location(region_code: str) -> str:
    """
    AWS 리전 코드를 Carbon Aware SDK location 코드로 변환

    Week 2 SDK 연동 시 사용 예정
    """
    region = get_region(region_code)
    return region["sdk_location"]