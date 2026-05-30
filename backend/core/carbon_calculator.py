from utils.converter import cpu_to_watts, watts_to_kwh, kwh_to_co2
from core.regions import get_region, get_tdp
from services.ai_service import get_current_intensity
from core.region_mapping import aws_to_azure
from utils.logger import get_logger

logger = get_logger(__name__)


def _get_intensity_with_fallback(region_code: str, region: dict) -> tuple[float, str]:
    """
    AI에서 실시간 탄소 강도 받아오고, 실패하면 고정값 사용
    
    Args:
        region_code: AWS 리전 코드 (예: "ap-northeast-2")
        region: get_region() 결과 딕셔너리
    
    Returns:
        (intensity, source) — source는 "ai" 또는 "fallback"
    """
    try:
        # AWS → Azure 코드 변환 (AI는 Azure 코드 사용)
        azure_zone = aws_to_azure(region_code)
        
        # AI 호출
        intensity = get_current_intensity(azure_zone)
        return intensity, "ai"
    
    except Exception as e:
        # 실패하면 고정값 사용
        logger.warning(
            f"AI 호출 실패, 고정값 사용 ({region_code}): {e}"
        )
        return float(region["carbon_intensity"]), "fallback"


# Prometheus scrape 간격 (seconds)
DEFAULT_DURATION_SEC = 15


def calculate_pod_co2(
    cpu_percent: float,
    memory_gb: float,
    instance_type: str,
    region_code: str,
    duration_sec: int = DEFAULT_DURATION_SEC,
) -> dict:

    # 1단계: 인스턴스 TDP 조회
    tdp = get_tdp(instance_type)

    # 2단계: CPU 사용률 → 전력(W) 변환
    watts = cpu_to_watts(cpu_percent, tdp)

    # 3단계: 전력(W) → 전력량(kWh) 변환
    kwh = watts_to_kwh(watts, duration_sec)

    # 4단계: 리전 정보 조회
    region = get_region(region_code)
    
    # 5단계: 탄소 강도 조회 (실시간 → fallback)
    intensity, intensity_source = _get_intensity_with_fallback(region_code, region)

    # 6단계: CO₂ 계산
    co2 = kwh_to_co2(kwh, region["pue"], intensity)

    return {
        "cpu_percent": cpu_percent,
        "memory_gb": memory_gb,
        "instance_type": instance_type,
        "region_code": region_code,
        "duration_sec": duration_sec,
        "region_name": region["name"],
        "tdp_watt": tdp,
        "pue": region["pue"],
        "carbon_intensity": intensity,
        "intensity_source": intensity_source,   # ★ 추가: "ai" or "fallback"
        "power_watt": round(watts, 4),
        "energy_kwh": round(kwh, 8),
        "co2_grams": round(co2, 6),
    }


def calculate_node_co2(
    cpu_percent: float,
    memory_gb: float,
    instance_type: str,
    region_code: str,
    duration_sec: int = DEFAULT_DURATION_SEC,
) -> dict:
    """
    노드(서버) 단위 CO₂ 계산

    현재는 calculate_pod_co2와 동일한 로직.
    추후 메모리·네트워크·스토리지 전력 추가 시 분리 예정.
    """
    return calculate_pod_co2(
        cpu_percent, memory_gb, instance_type, region_code, duration_sec
    )


def calculate_multiple_pods(
    pods: list[dict],
    node_cpu_total: float,
    instance_type: str,
    region_code: str,
    duration_sec: int = DEFAULT_DURATION_SEC,
) -> list[dict]:

    if node_cpu_total <= 0:
        raise ValueError(f"node_cpu_total은 0보다 커야 합니다: {node_cpu_total}")

    results = []
    for pod in pods:
        share = pod["cpu_percent"] / node_cpu_total

        pod_result = calculate_pod_co2(
            cpu_percent=pod["cpu_percent"],
            memory_gb=pod.get("memory_gb", 0),
            instance_type=instance_type,
            region_code=region_code,
            duration_sec=duration_sec,
        )

        pod_result["pod_name"] = pod["name"]
        pod_result["share_percent"] = round(share * 100, 2)
        results.append(pod_result)

    # CO₂ 많이 배출하는 순으로 정렬
    results.sort(key=lambda x: x["co2_grams"], reverse=True)
    return results