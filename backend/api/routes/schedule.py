from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/schedule", tags=["schedule"])


# ─── 요청/응답 스키마 ───────────────────────────────────────────────────────

class Recommendation(BaseModel):

    # AI가 보내는 필드
    best_zone: str = Field(..., description="최적 zone (예: 'US-MIDA-PJM')")
    opt_time: str = Field(..., description="최적 시작 시각 (ISO 8601)")
    opt_intensity: float = Field(..., description="최적 시각의 탄소 강도 (gCO₂/kWh)")
    all_zones: list[dict] = Field(..., description="모든 zone 비교 데이터")
    
    # 백엔드가 추가 (또는 AI가 같이 보내면 사용)
    pod_name: str = Field(..., description="추천 대상 파드 이름")
    pod_namespace: str = Field("default", description="K8s 네임스페이스")
    
    # 선택 필드
    reason: str = Field("", description="AI 추천 근거 (선택)")
    estimated_savings_g: float = Field(0.0, description="예상 CO₂ 절감량 (선택)")


class RecommendationResponse(BaseModel):
    status: str
    message: str
    saved_at: str


class ApplyScheduleRequest(BaseModel):
    """ CronJob 스케줄 변경 요청 """
    pod_name: str = Field(..., description="변경할 CronJob 이름")
    new_time: str = Field(..., description="새 실행 시각 (HH:MM)")
    namespace: str = Field("default", description="K8s 네임스페이스")


# ─── 메모리 저장소 ──────────────────────────────────────────────────────────
recommendations_history: list[dict] = []
schedule_changes: list[dict] = []


# ─── 유틸리티 함수 ─────────────────────────────────────────────────────────

def time_to_cron(time_str: str) -> str:
    """ "HH:MM" → cron 표현식 """
    try:
        hour, minute = time_str.split(":")
        hour_int = int(hour)
        minute_int = int(minute)
        if not (0 <= hour_int <= 23):
            raise ValueError(f"시간은 0~23 사이여야 합니다: {hour_int}")
        if not (0 <= minute_int <= 59):
            raise ValueError(f"분은 0~59 사이여야 합니다: {minute_int}")
        return f"{minute_int} {hour_int} * * *"
    except (ValueError, AttributeError) as e:
        raise ValueError(f"잘못된 시간 형식입니다 '{time_str}'. ({e})")


def iso_to_hhmm(iso_time: str) -> str:
    """ ISO 시각을 HH:MM으로 변환 (예: '2026-05-25 10:00:00+00:00' → '10:00') """
    try:
        dt = datetime.fromisoformat(iso_time.replace(" ", "T"))
        return dt.strftime("%H:%M")
    except Exception as e:
        raise ValueError(f"잘못된 ISO 시각 '{iso_time}': {e}")


def update_k8s_cronjob(namespace: str, name: str, new_schedule: str) -> dict:
    """ K8s CronJob 스케줄 변경 (현재 mock) """
    logger.info(f"[MOCK] K8s CronJob 변경: {namespace}/{name} → {new_schedule}")
    return {
        "name": name,
        "namespace": namespace,
        "new_schedule": new_schedule,
        "status": "applied (mock)",
    }


# ─── 추천 관련 엔드포인트 ──────────────────────────────────────────────────

@router.post("/recommend", response_model=RecommendationResponse)
def receive_recommendation(rec: Recommendation):
    """ AI팀 추천 결과 수신 """
    logger.info(
        f"AI 추천 수신: pod={rec.pod_name}, "
        f"best_zone={rec.best_zone}, opt_time={rec.opt_time}, "
        f"intensity={rec.opt_intensity}"
    )

    rec_data = rec.model_dump()
    rec_data["received_at"] = datetime.now(timezone.utc).isoformat()
    recommendations_history.append(rec_data)

    logger.info(f"추천 저장 완료 (총 {len(recommendations_history)}건)")
    return {
        "status": "success",
        "message": f"{rec.pod_name}에 대한 추천이 저장되었습니다",
        "saved_at": rec_data["received_at"],
    }


@router.get("/latest")
def get_latest_recommendation():
    """ 최신 추천 1건 조회 """
    if not recommendations_history:
        logger.warning("저장된 추천 없음 (404 반환)")
        raise HTTPException(status_code=404, detail="저장된 추천이 없습니다")
    return recommendations_history[-1]


@router.get("/history")
def get_recommendation_history(limit: int = 10):
    """ 추천 히스토리 조회 """
    return {
        "total": len(recommendations_history),
        "limit": limit,
        "items": list(reversed(recommendations_history))[:limit],
    }


# ─── CronJob 변경 엔드포인트 ────────────────────────────────────────────────

@router.post("/apply")
def apply_schedule(req: ApplyScheduleRequest):
    """ AI 추천 시각으로 K8s CronJob 스케줄 변경 """
    logger.info(f"CronJob 변경 요청: {req.namespace}/{req.pod_name} → {req.new_time}")

    try:
        new_cron = time_to_cron(req.new_time)
    except ValueError as e:
        logger.warning(f"잘못된 시간 형식: {req.new_time} - {e}")
        raise HTTPException(status_code=400, detail=str(e))

    k8s_result = update_k8s_cronjob(
        namespace=req.namespace,
        name=req.pod_name,
        new_schedule=new_cron,
    )

    change_record = {
        "pod_name": req.pod_name,
        "namespace": req.namespace,
        "requested_time": req.new_time,
        "applied_cron": new_cron,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "k8s_response": k8s_result,
    }
    schedule_changes.append(change_record)

    logger.info(f"CronJob 변경 완료: {req.pod_name}")
    return {
        "status": "success",
        "message": f"{req.pod_name}의 스케줄이 {req.new_time}로 변경되었습니다",
        "change": change_record,
    }


@router.get("/changes")
def get_change_history(limit: int = 10):
    """ CronJob 변경 이력 조회 """
    return {
        "total": len(schedule_changes),
        "limit": limit,
        "items": list(reversed(schedule_changes))[:limit],
    }


@router.delete("/history")
def clear_history():
    """ 히스토리 삭제 (개발/테스트용) """
    rec_count = len(recommendations_history)
    chg_count = len(schedule_changes)
    recommendations_history.clear()
    schedule_changes.clear()
    logger.info(f"히스토리 삭제: 추천 {rec_count}건, 변경 {chg_count}건")
    return {
        "status": "success",
        "deleted_recommendations": rec_count,
        "deleted_changes": chg_count,
    }
