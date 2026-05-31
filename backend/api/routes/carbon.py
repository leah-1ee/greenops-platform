from fastapi import APIRouter, HTTPException

from services.infra_service import get_node_metrics, get_pod_metrics
from core.carbon_calculator import calculate_pod_co2, calculate_multiple_pods
from schemas.carbon import NodeCarbonResponse, PodCarbonResponse
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/carbon", tags=["carbon"])


@router.get("/node")
def get_node_carbon():
    """ 노드 단위 실시간 CO₂ 조회 """
    logger.info("노드 탄소 조회 요청")

    try:
        metrics = get_node_metrics()
        result = calculate_pod_co2(
            cpu_percent=metrics["cpu_percent"],
            memory_gb=metrics["memory_gb"],
            instance_type=metrics["instance_type"],
            region_code=metrics["region_code"],
        )
        result["timestamp"] = metrics["timestamp"]
        result["source"] = metrics["source"]

        logger.info(f"노드 CO₂: {result['co2_grams']}g ({result['region_name']})")
        return result

    except Exception as e:
        logger.error(f"노드 탄소 계산 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pods")
def get_pod_carbon():
    """ 파드별 CO₂ 조회 (탄소 많은 순) """
    logger.info("파드 탄소 조회 요청")

    try:
        metrics = get_pod_metrics()
        pods = calculate_multiple_pods(
            pods=metrics["pods"],
            node_cpu_total=metrics["node_cpu_total"],
            instance_type=metrics["instance_type"],
            region_code=metrics["region_code"],
        )

        logger.info(f"{len(pods)}개 파드 탄소 계산 완료")
        return {
            "timestamp": metrics["timestamp"],
            "source": metrics["source"],
            "pods": pods,
        }

    except Exception as e:
        logger.error(f"파드 탄소 계산 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))