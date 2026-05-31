# ─── GreenOps Carbon Engine ──────────────────────────────────────────────────
# Multi-stage build: 최종 이미지 경량화

# ── 1단계: 의존성 설치 ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── 2단계: 런타임 이미지 ─────────────────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="GreenOps Team"
LABEL description="AI 기반 K8s 탄소 모니터링 및 그린 스케줄링 백엔드"

WORKDIR /app

# 의존성 복사
COPY --from=builder /install /usr/local

# 소스 코드 복사
COPY . .

# 환경 변수 기본값
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATA_SOURCE=prometheus
ENV LOG_LEVEL=INFO

EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=3).raise_for_status()"

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
