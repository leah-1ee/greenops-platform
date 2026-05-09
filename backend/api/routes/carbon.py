from fastapi import APIRouter
from services.infra_service import get_node_metrics, get_pod_metrics
from core.carbon_calculator import calculate_pod_co2, calculate_multiple_pods
from core.regions import REGION_DATA

# router 객체 생성 (FastAPI 객체 대신)
router = APIRouter(prefix="/carbon", tags=["carbon"])

@router.get("/node")
# 1. /node 엔드포인트
def get_node_carbon():
    # mock에서 노드 메트릭 가져오기
    metrics = get_node_metrics()
    
    # 탄소 계산
    result = calculate_pod_co2(
        cpu_percent=metrics["cpu_percent"],
        memory_gb=metrics["memory_gb"],
        instance_type=metrics["instance_type"],
        region_code=metrics["region_code"],
    )
    
    # timestamp랑 source도 같이 반환
    result["timestamp"] = metrics["timestamp"]
    result["source"] = metrics["source"]
    return result


@router.get("/pods")
# 2. /pods 엔드포인트
def get_pod_carbon():
    # mock에서 파드 메트릭 가져오기
    metrics = get_pod_metrics()
    
    # 여러 파드 한번에 계산
    pods = calculate_multiple_pods(
        pods=metrics["pods"],
        node_cpu_total=metrics["node_cpu_total"],
        instance_type=metrics["instance_type"],
        region_code=metrics["region_code"],
    )
    
    return {
        "timestamp": metrics["timestamp"],
        "source": metrics["source"],
        "pods": pods,
    }


@router.get("/regions")
# 3. /regions 엔드포인트
def get_supported_regions():
    return {"regions": REGION_DATA}