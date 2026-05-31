# ─── GreenOps AI Service ──────────────────────────────────────────────────────
# Multi-stage build: 최종 이미지 경량화

# ── 1단계: 의존성 설치 ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# requirements.txt만 먼저 복사해 레이어 캐시 활용
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── 2단계: 런타임 이미지 ─────────────────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="GreenOps Team"
LABEL description="LLM 기반 탄소 인식 스케줄링 추론 서비스"

WORKDIR /app

# 1단계에서 설치한 의존성만 복사 (pip 캐시 제외)
COPY --from=builder /install /usr/local

# 소스 코드 전체 복사
COPY . .

# 환경변수 기본값 (런타임 오버라이드 가능)
ENV HOST=0.0.0.0
ENV PORT=8001
ENV LOG_LEVEL=INFO

EXPOSE 8001

# 헬스체크: 30초 간격, 최대 3회 재시도
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health', timeout=3).raise_for_status()"

# uvicorn으로 ASGI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
