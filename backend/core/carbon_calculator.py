from utils.converter import cpu_to_watts, watts_to_kwh, kwh_to_co2
from core.regions import get_region, get_tdp

# Prometheus scrape 간격 (seconds)
DEFAULT_DURATION_SEC = 15


def calculate_pod_co2(
    cpu_percent: float,
    memory_gb: float,
    instance_type: str,
    region_code: str,
    duration_sec: int = DEFAULT_DURATION_SEC,
) -> dict:
    """
    파드 메트릭을 받아서 실시간 CO₂ 배출량을 계산

    Args:
        cpu_percent: CPU 사용률 (0~100)
        memory_gb: 메모리 사용량 (GB) — 현재는 참조만, 추후 메모리 전력 추가 예정
        instance_type: AWS 인스턴스 타입 (예: "t3.medium")
        region_code: AWS 리전 코드 (예: "ap-northeast-2")
        duration_sec: 측정 구간 길이 (기본 15초, Prometheus scrape 주기와 동일)

    Returns:
        계산 결과 딕셔너리:
        - cpu_percent, memory_gb, instance_type, region_code, duration_sec: 입력값
        - region_name: 리전 이름 (예: "서울")
        - tdp_watt: 인스턴스 TDP
        - power_watt: 실제 전력 소비 추정값
        - energy_kwh: 측정 구간 동안의 전력량
        - pue: 적용된 PUE
        - carbon_intensity: 적용된 탄소강도 (gCO₂/kWh)
        - co2_grams: 최종 CO₂ 배출량 (gCO₂) ★

    Raises:
        ValueError: 입력값이 유효 범위를 벗어난 경우
    """
    # 1단계: 인스턴스 TDP 조회
    tdp = get_tdp(instance_type)

    # 2단계: CPU 사용률 → 전력(W) 변환
    watts = cpu_to_watts(cpu_percent, tdp)

    # 3단계: 전력(W) → 전력량(kWh) 변환
    kwh = watts_to_kwh(watts, duration_sec)

    # 4단계: 리전 정보 조회 (PUE, 탄소강도)
    region = get_region(region_code)

    # 5단계: 전력량(kWh) → CO₂(g) 변환
    co2 = kwh_to_co2(kwh, region["pue"], region["carbon_intensity"])

    return {
        # 입력값 echo (디버깅 및 대시보드 활용)
        "cpu_percent": cpu_percent,
        "memory_gb": memory_gb,
        "instance_type": instance_type,
        "region_code": region_code,
        "duration_sec": duration_sec,
        # 메타데이터
        "region_name": region["name"],
        "tdp_watt": tdp,
        "pue": region["pue"],
        "carbon_intensity": region["carbon_intensity"],
        # 계산 결과
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
    """
    여러 파드의 CO₂를 한번에 계산 (CO₂ 많은 순으로 정렬)

    노드 전체 전력을 각 파드의 CPU 점유율로 배분.

    Args:
        pods: 파드 메트릭 리스트
              [{"name": "pod-a", "cpu_percent": 30, "memory_gb": 1.2}, ...]
        node_cpu_total: 노드 전체 CPU 사용률 (%)
        instance_type: 노드 인스턴스 타입
        region_code: 리전 코드
        duration_sec: 측정 구간

    Returns:
        파드별 계산 결과 리스트 (CO₂ 내림차순)
    """
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