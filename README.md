# GreenOps Platform

> AI 기반 Kubernetes 탄소 모니터링 및 그린 스케줄링 플랫폼

[![k3s](https://img.shields.io/badge/k3s-v1.35-blue)](https://k3s.io/)
[![Kepler](https://img.shields.io/badge/Kepler-0.8.0-green)](https://github.com/sustainable-computing-io/kepler)
[![Prometheus](https://img.shields.io/badge/Prometheus-v0.90-orange)](https://prometheus.io/)

---

## 개요

EU CSRD, K-ESG 등 ESG 공시 의무가 확대되면서 IT 인프라의 탄소 배출량 측정이 현실적 과제가 되었습니다. 그러나 Kubernetes 환경에서 Pod·서비스 단위의 탄소 배출량을 실시간으로 측정·추적하는 도구는 극히 부족합니다.

GreenOps Platform은 **Kepler eBPF 기반 Pod 단위 전력 측정**부터 **AI CronJob 스케줄 자동 최적화**까지 하나의 흐름으로 연결해, K8s 환경에서 탄소를 측정하고 실제로 줄일 수 있는 플랫폼입니다.

---

## 핵심 기능

- **Pod 단위 실시간 탄소 측정** — Kepler eBPF로 컨테이너 수준의 전력 소비를 15초 단위로 수집하고 지역별 탄소 계수로 CO₂ 환산
- **AI 그린 스케줄링** — 과거 워크로드 패턴 분석 → 탄소 집약 시간대 식별 → CronJob 실행 시각 자동 최적화
- **실시간 탄소 대시보드** — Grafana로 Pod·네임스페이스별 CO₂ 배출량 시각화 및 시간대별 히트맵 제공
- **Slack 알림** — 일일 탄소 요약 및 AI 스케줄링 최적화 제안 자동 전송
- **투명한 탄소 계수** — ElectricityMaps 기반 지역별 계수(서울·도쿄·버지니아)를 문서화하여 ESG 보고 신뢰성 확보

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                        GreenOps Pipeline                        │
│                                                                 │
│  ① 메트릭 수집          ② 탄소 환산          ③ 데이터 저장           │
│  ┌──────────┐           ┌──────────┐          ┌──────────┐      │
│  │  Kepler  │──────────▶│  탄소    │─────────▶│Prometheus│     │
│  │ (eBPF)   │  Pod 전력  │  환산    │  CO₂     │  TSDB    │      │
│  │Pod 단위  │  메트릭    │  엔진    │  메트릭   │          │       │
│  └──────────┘           └──────────┘          └──────────┘      │
│                              ↑                      │           │
│                         PUE × 탄소계수              │            │
│                         (Carbon Aware SDK)           ▼          │
│                                               ④ AI 스케줄링      │
│  ⑤ 대시보드·알림                              ┌──────────┐        │
│  ┌──────────┐                                 │ 패턴 분석 │      │
│  │ Grafana  │◀────────────────────────────────│ + LLM    │     │
│  │ 탄소     │          Slack 알림              │ CronJob  │      │
│  │ 대시보드  │─────────────────────────────▶   │ 최적화   │      │
│  └──────────┘                                 └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

| 단계 | 설명 |
|------|------|
| ① 메트릭 수집 | Kepler (eBPF)로 Pod 단위 전력 소비를 15초 단위 수집 |
| ② 탄소 환산 | Carbon Aware SDK로 조회한 지역별 탄소 계수(gCO₂/kWh) 적용 |
| ③ 데이터 저장 | Prometheus TSDB에 탄소 메트릭 저장, Pod·네임스페이스·시간대별 집계 |
| ④ AI 스케줄링 | 워크로드 패턴 분석 → CronJob 실행 시각 자동 최적화, LLM 자연어 리포트 |
| ⑤ 대시보드·알림 | Grafana 실시간 대시보드, Slack 알림 연동 |

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 컨테이너 오케스트레이션 | k3s |
| 배포 관리 | Helm Chart |
| 메트릭 수집 | Kepler (eBPF), kube-state-metrics, Node Exporter |
| 메트릭 저장·시각화 | kube-prometheus-stack (Prometheus + Alertmanager + Grafana) |
| 탄소 환산 엔진 | Python FastAPI (자체 개발) |
| 탄소 계수 조회 | Carbon Aware SDK + ElectricityMaps API |
| AI 스케줄링 엔진 | LLM API + 패턴 분석 로직 (자체 개발) |
| 프론트엔드 | React |
| 알림 | Slack Webhook API |

---

## 프로젝트 구조

```
greenops-platform/
├── infra/                        # 인프라 파트
│   ├── k3s/
│   │   ├── install.sh            # k3s + Helm 부트스트랩 스크립트
│   │   └── verify.sh             # 인프라 구성 검증 스크립트
│   ├── helm/
│   │   ├── prometheus/
│   │   │   └── values.yaml       # kube-prometheus-stack 설정
│   │   └── kepler/
│   │       └── values.yaml       # Kepler 설정
│   └── manifests/
│       ├── namespaces/           # 네임스페이스 정의
│       ├── rbac/                 # 파트별 RBAC 설정
│       ├── quotas/               # 파트별 리소스 쿼터
│       └── carbon-aware-sdk/     # Carbon Aware SDK 배포
├── backend/                      # 백엔드 파트 (FastAPI)
├── ai/                           # AI/데이터 파트
├── frontend/                     # 프론트엔드 파트 (React)
└── docs/                         # 프로젝트 문서
```

---

## 빠른 시작

### 사전 요구사항

- Ubuntu 22.04 이상 서버
- curl, bash

### 1. 인프라 부트스트랩

```bash
# k3s + Helm 설치 및 repo 등록
sudo ./infra/k3s/install.sh
source ~/.bashrc

# kubeconfig 권한 설정
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

### 2. 메트릭 스택 배포

```bash
# kube-prometheus-stack 배포 (Prometheus + Grafana)
helm install prometheus prometheus-community/kube-prometheus-stack \
  -f infra/helm/prometheus/values.yaml \
  -n monitoring --create-namespace

# Kepler DaemonSet 배포
helm install kepler kepler/kepler \
  -f infra/helm/kepler/values.yaml \
  -n kepler --create-namespace
```

### 3. 네임스페이스·RBAC·쿼터 설정

```bash
kubectl apply -f infra/manifests/namespaces/
kubectl apply -f infra/manifests/rbac/
kubectl apply -f infra/manifests/quotas/
```

### 4. Carbon Aware SDK 배포

```bash
# ElectricityMaps API 키 설정 (secret.yaml.template 복사 후 키 입력)
cp infra/manifests/carbon-aware-sdk/secret.yaml.template \
   infra/manifests/carbon-aware-sdk/secret.yaml
# secret.yaml에서 YOUR_API_KEY_HERE를 실제 키로 교체

kubectl apply -f infra/manifests/carbon-aware-sdk/secret.yaml
kubectl apply -f infra/manifests/carbon-aware-sdk/appsettings-configmap.yaml
kubectl apply -f infra/manifests/carbon-aware-sdk/deployment.yaml
kubectl apply -f infra/manifests/carbon-aware-sdk/service.yaml
```

### 5. 구성 검증

```bash
./infra/k3s/verify.sh
# 16/16 PASS 확인
```

### 6. Grafana 접속

SSH 터널 열기 (로컬 머신에서):
```bash
ssh -L 30300:localhost:30300 <서버접속정보>
```

브라우저에서 `http://localhost:30300` 접속
- ID: `admin`
- PW: `greenops` (운영 환경에서는 반드시 변경)

---

## 네임스페이스 구성

| 네임스페이스 | 용도 | 주요 권한 |
|---|---|---|
| `greenops-backend` | FastAPI 탄소 환산 서버 | CronJob update·patch |
| `greenops-ai` | AI 스케줄링 엔진 | CronJob 읽기 전용 |
| `greenops-front` | React UI | Pod 조회 (최소 권한) |
| `greenops-infra` | Carbon Aware SDK | ConfigMap 읽기 |
| `monitoring` | Prometheus·Grafana | — |
| `kepler` | Kepler DaemonSet | — |

---

## MVP 범위

| 영역 | 내용 |
|------|------|
| 메트릭 수집 | Kepler DaemonSet으로 Pod 단위 전력 소비 실시간 수집 |
| 탄소 환산 | 서울·도쿄·버지니아 리전 계수 적용, 실시간 CO₂ 환산 |
| 대시보드 | Grafana — Pod·네임스페이스별 CO₂ 실시간 시각화, 시간대별 히트맵 |
| AI 그린 스케줄링 | 배치 Job/CronJob 대상, 탄소 절감 예상 시각 Top 3 제안 및 자동 업데이트 |
| Slack 알림 | 일일 탄소 요약 및 스케줄링 최적화 제안 메시지 자동 전송 |

### Post-MVP 확장 계획

- Carbon-Aware Pod 배치 스케줄링 (K8s Scheduler Plugin)
- ESG 리포트 PDF 자동 생성
- 멀티클라우드 지원 (GCP·Azure)
- Namespace별 탄소 과금
- 월간 탄소 예산 관리

---

## 팀 구성 및 역할

| 역할 | 주요 담당 |
|------|----------|
| 인프라 | k3s 클러스터, Kepler·Prometheus 배포, Carbon Aware SDK, RBAC·네임스페이스 |
| 백엔드 | 전력→CO₂ 환산 FastAPI, Prometheus 커스텀 메트릭, CronJob 자동 업데이트 API |
| AI/데이터 | 최적 시점 추천 알고리즘, 스케줄링 추천 API, Slack 알림 연동 |
| 프론트·시각화 | Grafana 대시보드, React UI, 데이터 시각화 |

---