import random
import requests
from datetime import datetime, timezone

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


# 시스템 프로세스 (Kepler가 보고하는 비-K8s 파드)
EXCLUDED_POD_NAMES = ["unknown", "kernel_processes", "system_processes"]


MOCK_POD_PROFILES = [
    {"name": "greenops-api-server",  "base_cpu": 35, "base_mem": 1.5},
    {"name": "greenops-database",    "base_cpu": 25, "base_mem": 2.0},
    {"name": "greenops-worker",      "base_cpu": 15, "base_mem": 0.8},
    {"name": "greenops-frontend",    "base_cpu": 10, "base_mem": 0.5},
    {"name": "greenops-ai-engine",   "base_cpu": 20, "base_mem": 1.2},
]


# ─── Prometheus 쿼리 헬퍼 ───────────────────────────────────────────────────

def _query_prometheus(query: str) -> list:
    """ Prometheus에 PromQL 쿼리 실행하고 결과 반환 """
    try:
        response = requests.get(
            f"{settings.prometheus_url}/api/v1/query",
            params={"query": query},
            timeout=settings.prometheus_timeout_sec,
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] != "success":
            logger.error(f"Prometheus 쿼리 실패: {data}")
            return []

        return data["data"]["result"]

    except requests.exceptions.RequestException as e:
        logger.error(f"Prometheus 호출 실패: {e}")
        raise


# ─── 노드 메트릭 ────────────────────────────────────────────────────────────

def get_node_metrics() -> dict:
    """ 노드(서버) 단위 메트릭 반환 """
    logger.debug(f"노드 메트릭 수집 (source={settings.data_source})")

    if settings.data_source == "mock":
        return _get_node_metrics_mock()
    elif settings.data_source == "prometheus":
        return _get_node_metrics_prometheus()
    else:
        raise ValueError(f"알 수 없는 data_source: {settings.data_source}")


def _get_node_metrics_mock() -> dict:
    return {
        "cpu_percent": round(random.uniform(40, 85), 2),
        "memory_gb": round(random.uniform(6, 12), 2),
        "instance_type": settings.default_instance_type,
        "region_code": settings.default_region,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
    }


def _get_node_metrics_prometheus() -> dict:
    """
    노드 전체 메트릭 산출

    파드별 Kepler 전력을 합산 (시스템 프로세스 제외).
    파드 메트릭과 동일한 필터링 적용해 일관성 유지.
    """
    query = 'sum by (pod_name) (rate(kepler_container_joules_total[1m]))'
    results = _query_prometheus(query)

    if not results:
        logger.warning("노드 메트릭 없음, 0으로 처리")
        return {
            "cpu_percent": 0.0,
            "memory_gb": 0.0,
            "instance_type": settings.default_instance_type,
            "region_code": settings.default_region,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "prometheus",
        }

    # 시스템 프로세스 제외하고 합산
    total_watts = 0.0
    for item in results:
        pod_name = item["metric"].get("pod_name", "unknown")
        watts = float(item["value"][1])

        if pod_name in EXCLUDED_POD_NAMES or watts <= 0:
            continue

        total_watts += watts

    # Watt → CPU% 역산 (TDP 기준)
    from core.regions import get_tdp
    tdp = get_tdp(settings.default_instance_type)
    cpu_percent = min(100, (total_watts / tdp) * 100) if tdp > 0 else 0

    logger.info(
        f"노드 메트릭 (Kepler 합계, 시스템 제외): "
        f"전력 {total_watts:.2f}W, CPU {cpu_percent:.2f}%"
    )

    return {
        "cpu_percent": round(cpu_percent, 2),
        "memory_gb": 0.0,
        "instance_type": settings.default_instance_type,
        "region_code": settings.default_region,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "prometheus",
    }


# ─── 파드 메트릭 ────────────────────────────────────────────────────────────

def get_pod_metrics() -> dict:
    """ 파드별 메트릭 반환 """
    logger.debug(f"파드 메트릭 수집 (source={settings.data_source})")

    if settings.data_source == "mock":
        return _get_pod_metrics_mock()
    elif settings.data_source == "prometheus":
        return _get_pod_metrics_prometheus()
    else:
        raise ValueError(f"알 수 없는 data_source: {settings.data_source}")


def _get_pod_metrics_mock() -> dict:
    pods = []
    node_cpu_total = 0.0

    for profile in MOCK_POD_PROFILES:
        cpu = round(random.uniform(
            profile["base_cpu"] * 0.7,
            profile["base_cpu"] * 1.3
        ), 2)
        mem = round(random.uniform(
            profile["base_mem"] * 0.8,
            profile["base_mem"] * 1.2
        ), 2)
        pods.append({
            "name": profile["name"],
            "cpu_percent": cpu,
            "memory_gb": mem,
        })
        node_cpu_total += cpu

    return {
        "pods": pods,
        "node_cpu_total": round(node_cpu_total, 2),
        "instance_type": settings.default_instance_type,
        "region_code": settings.default_region,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
    }


def _get_pod_metrics_prometheus() -> dict:
    """
    Kepler 메트릭에서 파드별 전력 데이터 조회
    시스템 프로세스(kernel_processes, system_processes)는 제외.
    """
    query = 'sum by (pod_name) (rate(kepler_container_joules_total[1m]))'
    results = _query_prometheus(query)

    if not results:
        logger.warning("Kepler 메트릭이 없습니다. mock으로 fallback.")
        return _get_pod_metrics_mock()

    pods = []
    node_power_total = 0.0

    for item in results:
        pod_name = item["metric"].get("pod_name", "unknown")
        watts = float(item["value"][1])

        if pod_name in EXCLUDED_POD_NAMES or watts <= 0:
            continue

        # Watt → CPU% 역산 (TDP 기준)
        from core.regions import get_tdp
        tdp = get_tdp(settings.default_instance_type)
        cpu_percent = min(100, (watts / tdp) * 100) if tdp > 0 else 0

        pods.append({
            "name": pod_name,
            "cpu_percent": round(cpu_percent, 2),
            "memory_gb": 0,
        })
        node_power_total += watts

    # 노드 전체 CPU% (역산)
    from core.regions import get_tdp
    tdp = get_tdp(settings.default_instance_type)
    node_cpu_total = min(100, (node_power_total / tdp) * 100) if tdp > 0 else 0

    logger.info(
        f"Prometheus 파드 메트릭: {len(pods)}개 파드, "
        f"노드 전력 {node_power_total:.2f}W"
    )

    return {
        "pods": pods,
        "node_cpu_total": round(node_cpu_total, 2),
        "instance_type": settings.default_instance_type,
        "region_code": settings.default_region,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "prometheus",
    }