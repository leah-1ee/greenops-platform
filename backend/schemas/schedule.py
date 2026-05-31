from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    """ AI팀이 보내는 추천 결과 """
    pod_name: str = Field(..., description="추천 대상 파드 이름")
    suggested_times: list[str] = Field(..., description="추천 시간대 Top 3 (HH:MM)")
    estimated_savings_g: float = Field(..., description="예상 절감 CO₂ (g)")
    reason: str = Field(..., description="AI 추천 근거")


class RecommendationResponse(BaseModel):
    """ 추천 수신 응답 """
    status: str
    message: str
    saved_at: str


class ApplyScheduleRequest(BaseModel):
    """ CronJob 스케줄 변경 요청 """
    pod_name: str = Field(..., description="변경할 CronJob 이름")
    new_time: str = Field(..., description="새 실행 시각 (HH:MM)")
    namespace: str = Field("default", description="K8s 네임스페이스")


class ScheduleChangeRecord(BaseModel):
    """ CronJob 변경 이력 """
    pod_name: str
    namespace: str
    requested_time: str
    applied_cron: str
    changed_at: str
    k8s_response: dict


class ApplyScheduleResponse(BaseModel):
    """ 스케줄 적용 응답 """
    status: str
    message: str
    change: ScheduleChangeRecord


class HistoryResponse(BaseModel):
    """ 히스토리 조회 응답 """
    total: int
    limit: int
    items: list[dict]
