# GreenOps 인프라 설정 가이드

전체 인프라를 빠르게 설정하기 위한 명령어 중심 가이드.

## 사전 준비

- ElectricityMaps API 키를 팀 관리자에게 받아둘 것
- GitHub 접근 권한 확인

---

## Step 1. 서버 접속 및 레포 클론 

```bash
git clone https://github.com/leah-1ee/greenops-platform.git
cd greenops-platform
```

---

## Step 2. Docker 설치 

```bash
sudo apt install docker.io -y
sudo usermod -aG docker $USER
newgrp docker
```

---

## Step 3. 자동 설치 (k3s + Helm) 

```bash
sudo ./infra/k3s/install.sh
source ~/.bashrc
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

---

## Step 4. 스택 배포 

```bash
# 1. Prometheus 스택
helm install prometheus prometheus-community/kube-prometheus-stack \
  -f infra/helm/prometheus/values.yaml \
  -n monitoring --create-namespace

# 2. Kepler
helm install kepler kepler/kepler \
  -f infra/helm/kepler/values.yaml \
  -n kepler --create-namespace

# 3. 네임스페이스 / RBAC / ResourceQuota
kubectl apply -f infra/manifests/namespaces/
kubectl apply -f infra/manifests/rbac/
kubectl apply -f infra/manifests/quotas/

# 4. Carbon Aware SDK Secret 생성 (YOUR_API_KEY_HERE → 실제 키로 교체)
cp infra/manifests/carbon-aware-sdk/secret.yaml.template \
   infra/manifests/carbon-aware-sdk/secret.yaml
vi infra/manifests/carbon-aware-sdk/secret.yaml
kubectl apply -f infra/manifests/carbon-aware-sdk/

# 5. AI Secret 생성 (YOUR_API_KEY_HERE → 실제 키로 교체)
cp infra/manifests/ai/secret.yaml.template \
   infra/manifests/ai/secret.yaml
vi infra/manifests/ai/secret.yaml
```

---

## Step 5. 서비스 이미지 빌드 및 배포 

```bash
# 백엔드
docker build -t greenops-backend:latest ./backend/
sudo k3s ctr images import <(docker save greenops-backend:latest)
docker rmi greenops-backend:latest
kubectl apply -f infra/manifests/backend/

# AI
docker build -t greenops-ai:latest ./ai-data/
sudo k3s ctr images import <(docker save greenops-ai:latest)
docker rmi greenops-ai:latest
kubectl apply -f infra/manifests/ai/

# 프론트
docker build --build-arg VITE_API_BASE_URL=/api -t greenops-frontend:latest ./frontend/
sudo k3s ctr images import <(docker save greenops-frontend:latest)
docker rmi greenops-frontend:latest
kubectl apply -f infra/manifests/frontend/
```

---

## Step 6. 검증 

```bash
./infra/k3s/verify.sh
```

21/21 PASS 확인.

---

## 주의사항

- `docker system prune` 사용 시 `-af` 옵션 절대 금지 (`-f`만 사용)
  → `-a` 옵션이 k3s containerd 이미지까지 삭제함
- 디스크 여유 공간 5GB 이상 유지 권장
