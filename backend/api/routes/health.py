from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """ 서버 헬스체크 — 200 OK + status 응답 """
    return {"status": "ok"}