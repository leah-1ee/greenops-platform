#!/usr/bin/env bash
# GreenOps 1주차 인프라 구성 검증 스크립트
#
# 사용법:
#   chmod +x infra/k3s/verify.sh
#   ./infra/k3s/verify.sh
#
# 종료 코드:
#   0 - 모든 항목 PASS
#   1 - 하나 이상 FAIL

set -uo pipefail

FAIL_COUNT=0
TOTAL=10

pass() { echo "  ✅ PASS: $1"; }
fail() { echo "  ❌ FAIL: $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# ─── [1/10] k3s 설치 확인 ────────────────────────────────────────────────────
echo "[1/${TOTAL}] k3s 설치 확인"
if command -v k3s &>/dev/null; then
  pass "k3s 설치됨 ($(k3s --version 2>/dev/null | head -1))"
else
  fail "k3s 명령어를 찾을 수 없음"
fi

# ─── [2/10] kubectl 노드 Ready 확인 ──────────────────────────────────────────
echo "[2/${TOTAL}] kubectl 노드 Ready 확인"
if kubectl get nodes 2>/dev/null | grep -q " Ready"; then
  pass "노드가 Ready 상태"
  kubectl get nodes 2>/dev/null | grep -v "^NAME" | awk '{printf "         %s  %s\n", $1, $2}'
else
  fail "Ready 상태인 노드 없음 (kubectl get nodes 확인 필요)"
fi

# ─── [3/10] Helm 설치 확인 ───────────────────────────────────────────────────
echo "[3/${TOTAL}] Helm 설치 확인"
if command -v helm &>/dev/null; then
  pass "Helm 설치됨 ($(helm version --short 2>/dev/null))"
else
  fail "helm 명령어를 찾을 수 없음"
fi

# ─── [4/10] Helm repo 등록 확인 ──────────────────────────────────────────────
echo "[4/${TOTAL}] Helm repo 등록 확인 (prometheus-community, kepler)"
REPO_LIST=$(helm repo list 2>/dev/null || true)
for repo in prometheus-community kepler; do
  if echo "$REPO_LIST" | grep -q "^${repo}"; then
    pass "repo '${repo}' 등록됨"
  else
    fail "repo '${repo}' 등록되지 않음"
  fi
done

# ─── [5/10] kube-prometheus-stack 배포 확인 ──────────────────────────────────
echo "[5/${TOTAL}] kube-prometheus-stack 배포 확인 (namespace: monitoring)"
if helm list -n monitoring 2>/dev/null | grep -q "prometheus"; then
  pass "prometheus 릴리즈 배포됨"
else
  fail "monitoring 네임스페이스에 prometheus 릴리즈 없음"
fi

# ─── [6/10] Grafana Pod Running 확인 ─────────────────────────────────────────
echo "[6/${TOTAL}] Grafana Pod Running 확인"
GRAFANA_POD=$(kubectl get pods -n monitoring 2>/dev/null | grep "grafana" | grep "Running" | head -1)
if [ -n "$GRAFANA_POD" ]; then
  pass "Grafana Pod Running 확인됨 ($(echo "$GRAFANA_POD" | awk '{print $1}'))"
else
  GRAFANA_ANY=$(kubectl get pods -n monitoring 2>/dev/null | grep "grafana" | head -1)
  if [ -n "$GRAFANA_ANY" ]; then
    STATUS=$(echo "$GRAFANA_ANY" | awk '{print $3}')
    fail "Grafana Pod 존재하나 Running 아님 (현재 상태: ${STATUS})"
  else
    fail "monitoring 네임스페이스에서 grafana Pod를 찾을 수 없음"
  fi
fi

# ─── [7/10] Kepler 배포 확인 ─────────────────────────────────────────────────
echo "[7/${TOTAL}] Kepler 배포 확인 (namespace: kepler)"
if helm list -n kepler 2>/dev/null | grep -q "kepler"; then
  pass "kepler 릴리즈 배포됨"
else
  fail "kepler 네임스페이스에 kepler 릴리즈 없음"
fi

# ─── [8/10] Kepler Pod Running 확인 ──────────────────────────────────────────
echo "[8/${TOTAL}] Kepler Pod Running 확인"
KEPLER_POD=$(kubectl get pods -n kepler 2>/dev/null | grep "kepler" | grep "Running" | head -1)
if [ -n "$KEPLER_POD" ]; then
  pass "Kepler Pod Running 확인됨 ($(echo "$KEPLER_POD" | awk '{print $1}'))"
else
  KEPLER_ANY=$(kubectl get pods -n kepler 2>/dev/null | grep "kepler" | head -1)
  if [ -n "$KEPLER_ANY" ]; then
    STATUS=$(echo "$KEPLER_ANY" | awk '{print $3}')
    fail "Kepler Pod 존재하나 Running 아님 (현재 상태: ${STATUS})"
  else
    fail "kepler 네임스페이스에서 kepler Pod를 찾을 수 없음"
  fi
fi

# ─── [9/10] Kepler ServiceMonitor Prometheus 노출 확인 ───────────────────────
echo "[9/${TOTAL}] Kepler ServiceMonitor 등록 확인"
if kubectl get servicemonitor -n kepler 2>/dev/null | grep -qi "kepler"; then
  pass "Kepler ServiceMonitor 등록됨"
else
  fail "kepler 네임스페이스에 kepler ServiceMonitor 없음 (Prometheus가 scrape 못할 수 있음)"
fi

# ─── [10/10] kepler_container_joules_total 메트릭 수집 확인 ──────────────────
echo "[10/${TOTAL}] kepler_container_joules_total 메트릭 수집 확인"
KEPLER_METRICS_POD=$(kubectl get pods -n kepler \
  -l app.kubernetes.io/name=kepler \
  -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)

if [ -z "$KEPLER_METRICS_POD" ]; then
  fail "Kepler Pod를 찾을 수 없음 (메트릭 수집 확인 불가)"
else
  METRICS_RESULT=$(kubectl exec -n kepler "$KEPLER_METRICS_POD" \
    -- curl -s --max-time 10 http://localhost:9102/metrics 2>/dev/null || true)

  if [ -z "$METRICS_RESULT" ]; then
    fail "Kepler Pod 내 curl 실행 실패 (curl이 설치되지 않았거나 :9102 포트 미응답)"
  elif echo "$METRICS_RESULT" | grep -q "kepler_container_joules_total"; then
    pass "kepler_container_joules_total 메트릭 확인됨 (Pod: ${KEPLER_METRICS_POD})"
  else
    fail "kepler_container_joules_total 메트릭이 출력에 없음 (eBPF 수집 미시작 가능성)"
  fi
fi

# ─── 최종 결과 ────────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────────"
PASS_COUNT=$((TOTAL - FAIL_COUNT))
echo "결과: ${PASS_COUNT}/${TOTAL} 항목 PASS"
if [ "$FAIL_COUNT" -eq 0 ]; then
  echo "🎉 모든 항목 PASS - 1주차 인프라 구성 완료!"
  exit 0
else
  echo "⚠️  ${FAIL_COUNT}개 항목 FAIL - 위 FAIL 항목을 확인하세요."
  exit 1
fi
