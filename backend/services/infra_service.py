"""
인프라 서비스 — 메트릭 데이터 수집

    이 파일의 함수들을 Prometheus API 호출 코드로 교체
    → calculator, router 등 다른 코드는 변경 불필요
"""

import random
from datetime import datetime, timezone


# ─── 설정값 ────────────────────────────────────────────────────────────────
# 인프라팀과 합의된 실제 값으로 추후 교체
DEFAULT_INSTANCE_TYPE = "t3.medium"
DEFAULT_REGION_CODE = "ap-northeast-2"   # 서울

# 가상 파드 목록 (실제 K8s 클러스터에서는 Prometheus가 자동으로 알려줌)
MOCK_POD_PROFILES = [
    {"name": "greenops-api-server",  "base_cpu": 35, "base_mem": 1.5},
    {"name": "greenops-database",    "base_cpu": 25, "base_mem": 2.0},
    {"name": "greenops-worker",      "base_cpu": 15, "base_mem": 0.8},
    {"name": "greenops-frontend",    "base_cpu": 10, "base_mem": 0.5},
    {"name": "greenops-ai-engine",   "base_cpu": 20, "base_mem": 1.2},
]


# ─── 노드 메트릭 ────────────────────────────────────────────────────────────

def get_node_metrics() -> dict:
    """
    노드(서버) 단위 메트릭 반환

    Returns:
        - cpu_percent: 노드 CPU 사용률 (40~85% 랜덤)
        - memory_gb: 노드 메모리 사용량 (6~12GB 랜덤)
        - instance_type: 인스턴스 타입
        - region_code: 리전 코드
        - timestamp: ISO 8601 형식 시각
        - source: 데이터 출처 ("mock" | "prometheus")
    """
    return {
        "cpu_percent": round(random.uniform(40, 85), 2),
        "memory_gb": round(random.uniform(6, 12), 2),
        "instance_type": DEFAULT_INSTANCE_TYPE,
        "region_code": DEFAULT_REGION_CODE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
    }


# ─── 파드 메트릭 ────────────────────────────────────────────────────────────

def get_pod_metrics() -> dict:
    """
    파드별 메트릭 반환

    Returns:
        - pods: 파드 메트릭 리스트
                [{"name": str, "cpu_percent": float, "memory_gb": float}, ...]
        - node_cpu_total: 노드 전체 CPU 사용률 합계
        - instance_type: 인스턴스 타입
        - region_code: 리전 코드
        - timestamp: ISO 8601 형식 시각
        - source: 데이터 출처
    """
    pods = []
    node_cpu_total = 0.0

    for profile in MOCK_POD_PROFILES:
        # 베이스 값 ±30% 범위에서 랜덤 변동
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
        "instance_type": DEFAULT_INSTANCE_TYPE,
        "region_code": DEFAULT_REGION_CODE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
    }


# ─── 추후 Prometheus 연동 시 교체될 함수 (현재는 NotImplementedError) ────────

def fetch_from_prometheus(query: str) -> dict:
    """
    Prometheus PromQL 쿼리 실행 (Week 2 구현 예정)

    Args:
        query: PromQL 쿼리 문자열
               (예: 'kepler_container_joules_total')

    TODO: requests 라이브러리로 Prometheus HTTP API 호출
        url = f"{PROMETHEUS_URL}/api/v1/query"
        response = requests.get(url, params={"query": query})
        return response.json()
    """
    raise NotImplementedError(
        "Prometheus 연동은 Week 2 인프라 구축 완료 후 구현됩니다."
    )
