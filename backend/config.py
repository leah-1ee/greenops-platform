from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ 서버 전역 설정 """

    # ─── 앱 메타 정보 ──────────────────────────────────────────────────────
    app_name: str = "GreenOps Carbon Engine"
    app_version: str = "0.1.0"
    app_description: str = "AI 기반 K8s 탄소 모니터링 및 그린 스케줄링 백엔드"

    # ─── 서버 설정 ─────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = ["*"]   # 운영 시 특정 도메인으로 제한

    # ─── Prometheus 연동  ────────────────────────────────────
    prometheus_url: str = "http://localhost:9090"
    prometheus_timeout_sec: int = 10

    # ─── Carbon Aware SDK 연동 ──────────────────────────────
    carbon_aware_sdk_url: str = "http://localhost:8080"
    carbon_aware_sdk_timeout_sec: int = 5

    # ─── AI팀 서버 연동 ────────────────────────────────────────────────────
    ai_service_url: str = "http://localhost:8001"

    # ─── 메트릭 수집 설정 ──────────────────────────────────────────────────
    scrape_interval_sec: int = 15      # Prometheus scrape 주기와 동일
    default_region: str = "ap-northeast-2"
    default_instance_type: str = "t3.medium"

    # ─── K8s 연동  ────────────────────────────────────────────
    k8s_in_cluster: bool = False        # 클러스터 내 실행 여부
    k8s_default_namespace: str = "default"

    # ─── 데이터 소스 모드 ──────────────────────────────────────────────────

    data_source: str = "mock"

    # ─── 로깅 설정 ─────────────────────────────────────────────────────────
    log_level: str = "INFO"             # DEBUG, INFO, WARNING, ERROR

    # ─── pydantic-settings 설정 ────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,    # PORT, port 모두 인식
        extra="ignore",          # .env에 알 수 없는 키 있어도 무시
    )


# 전역 인스턴스 — 다른 모듈에서 `from config import settings` 로 사용
settings = Settings()