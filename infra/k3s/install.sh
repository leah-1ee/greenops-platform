#!/usr/bin/env bash
# GreenOps 인프라 부트스트랩 스크립트
#
# 사용법:
#   chmod +x infra/k3s/install.sh
#   ./infra/k3s/install.sh
#
# 전제 조건: curl, bash 설치된 Ubuntu/Debian 계열 서버
# 실행 후 새 터미널을 열거나 `source ~/.bashrc` 로 KUBECONFIG를 활성화하세요.

set -euo pipefail

# ─── 1. k3s 설치 ─────────────────────────────────────────────────────────────
echo "[1/5] k3s 설치 확인 중..."
if command -v k3s &>/dev/null; then
  echo "  → k3s 이미 설치됨, skip"
else
  echo "  → k3s 설치 시작 (traefik 비활성화)"
  curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik" sh -
  echo "  → k3s 설치 완료"
fi

# ─── 2. kubeconfig 환경변수 설정 ──────────────────────────────────────────────
echo "[2/5] KUBECONFIG 환경변수 설정 중..."
KUBECONFIG_LINE='export KUBECONFIG=/etc/rancher/k3s/k3s.yaml'
touch ~/.bashrc
if grep -qF "$KUBECONFIG_LINE" ~/.bashrc; then
  echo "  → ~/.bashrc에 이미 설정됨, skip"
else
  echo "$KUBECONFIG_LINE" >> ~/.bashrc
  echo "  → ~/.bashrc에 KUBECONFIG 추가 완료"
fi
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# ─── 3. k3s 노드 Ready 대기 ──────────────────────────────────────────────────
echo "[3/5] k3s 노드 Ready 대기 중..."
TIMEOUT=120
ELAPSED=0
until kubectl get nodes 2>/dev/null | grep -q " Ready"; do
  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "  ✗ 타임아웃: ${TIMEOUT}s 안에 노드가 Ready 상태가 되지 않았습니다." >&2
    exit 1
  fi
  echo "  → 대기 중... (${ELAPSED}s / ${TIMEOUT}s)"
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done
echo "  → 노드 Ready 확인됨"
kubectl get nodes

# ─── 4. Helm 설치 ────────────────────────────────────────────────────────────
echo "[4/5] Helm 설치 확인 중..."
if command -v helm &>/dev/null; then
  echo "  → Helm 이미 설치됨 ($(helm version --short)), skip"
else
  echo "  → Helm 설치 시작"
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
  echo "  → Helm 설치 완료"
fi

# ─── 5. Helm repo 등록 및 업데이트 ───────────────────────────────────────────
echo "[5/5] Helm repo 등록 및 업데이트 중..."

add_repo() {
  local name="$1"
  local url="$2"
  if helm repo list 2>/dev/null | grep -q "^${name}"; then
    echo "  → repo '${name}' 이미 등록됨, skip"
  else
    helm repo add "$name" "$url"
    echo "  → repo '${name}' 등록 완료"
  fi
}

add_repo prometheus-community https://prometheus-community.github.io/helm-charts
add_repo kepler              https://sustainable-computing-io.github.io/kepler-helm-chart

helm repo update
echo "  → Helm repo 업데이트 완료"

echo ""
echo "✅ 부트스트랩 완료!"
echo "   다음 단계:"
echo "   source ~/.bashrc"
echo "   helm install prometheus prometheus-community/kube-prometheus-stack -f infra/helm/prometheus/values.yaml -n monitoring --create-namespace"
echo "   helm install kepler kepler/kepler -f infra/helm/kepler/values.yaml -n kepler --create-namespace"
