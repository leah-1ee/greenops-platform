from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from schemas.schedule import (
    Recommendation,
    RecommendationResponse,
    ApplyScheduleRequest,
)

router = APIRouter(prefix="/schedule", tags=["schedule"])


# ─── 메모리 저장소 ──────────────────────────────────────────────────────────
recommendations_history: list[dict] = []
schedule_changes: list[dict] = []


# ─── 유틸리티 함수 ─────────────────────────────────────────────────────────

def time_to_cron(time_str: str) -> str:
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


def update_k8s_cronjob(namespace: str, name: str, new_schedule: str) -> dict:

    return {
        "name": name,
        "namespace": namespace,
        "new_schedule": new_schedule,
        "status": "applied (mock)",
    }


# ─── 추천 관련 엔드포인트 ──────────────────────────────────────────────────

@router.post("/recommend", response_model=RecommendationResponse)
def receive_recommendation(rec: Recommendation):
    """ AI팀에서 추천 결과 수신 """
    rec_data = rec.model_dump()
    rec_data["received_at"] = datetime.now(timezone.utc).isoformat()
    recommendations_history.append(rec_data)

    return {
        "status": "success",
        "message": f"{rec.pod_name}에 대한 추천이 저장되었습니다",
        "saved_at": rec_data["received_at"],
    }


@router.get("/latest")
def get_latest_recommendation():
    """ 가장 최신 추천 1건 조회 """
    if not recommendations_history:
        raise HTTPException(status_code=404, detail="저장된 추천이 없습니다")
    return recommendations_history[-1]


@router.get("/history")
def get_recommendation_history(limit: int = 10):
    """ 추천 히스토리 조회 (최신 순) """
    sorted_history = list(reversed(recommendations_history))
    return {
        "total": len(recommendations_history),
        "limit": limit,
        "items": sorted_history[:limit],
    }


# ─── CronJob 변경 엔드포인트 (F-23 Must) ────────────────────────────────────

@router.post("/apply")
def apply_schedule(req: ApplyScheduleRequest):
    # 1. cron 표현식 생성
    try:
        new_cron = time_to_cron(req.new_time)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. K8s CronJob 변경 (mock)
    k8s_result = update_k8s_cronjob(
        namespace=req.namespace,
        name=req.pod_name,
        new_schedule=new_cron,
    )

    # 3. 변경 이력 저장
    change_record = {
        "pod_name": req.pod_name,
        "namespace": req.namespace,
        "requested_time": req.new_time,
        "applied_cron": new_cron,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "k8s_response": k8s_result,
    }
    schedule_changes.append(change_record)

    return {
        "status": "success",
        "message": f"{req.pod_name}의 스케줄이 {req.new_time}로 변경되었습니다",
        "change": change_record,
    }


@router.get("/changes")
def get_change_history(limit: int = 10):
    """ CronJob 변경 이력 조회 (최신 순) """
    sorted_changes = list(reversed(schedule_changes))
    return {
        "total": len(schedule_changes),
        "limit": limit,
        "items": sorted_changes[:limit],
    }


@router.delete("/history")
def clear_history():
    """ 히스토리 전체 삭제 (개발/테스트용) """
    rec_count = len(recommendations_history)
    chg_count = len(schedule_changes)
    recommendations_history.clear()
    schedule_changes.clear()
    return {
        "status": "success",
        "deleted_recommendations": rec_count,
        "deleted_changes": chg_count,
    }