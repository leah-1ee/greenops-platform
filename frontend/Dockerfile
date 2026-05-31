# ─── GreenOps Frontend ────────────────────────────────────────────────────────
# Multi-stage build: Node.js로 빌드 → nginx로 정적 파일 서빙

# ── 1단계: 빌드 (builder) ─────────────────────────────────────────────────────
FROM node:20-slim AS builder

WORKDIR /app

# package.json / package-lock.json만 먼저 복사해 레이어 캐시 활용
COPY package.json package-lock.json ./

# ci: package-lock.json을 기준으로 재현 가능한 설치 (npm install보다 안전)
RUN npm ci

# 소스 코드 전체 복사 후 정적 파일 빌드
# VITE_API_BASE_URL 등 VITE_ 접두사 환경변수는 이 단계에서 주입해야 한다.
# 예: docker build --build-arg VITE_API_BASE_URL=http://... 후 ARG/ENV 처리
COPY . .
RUN npm run build

# ── 2단계: 런타임 (nginx) ─────────────────────────────────────────────────────
FROM nginx:alpine

LABEL maintainer="GreenOps Team"
LABEL description="React/Vite SPA 정적 파일 서버"

# SPA 라우팅 지원: 모든 경로를 index.html로 폴백
# nginx.conf 인라인 작성 후 기본 설정 파일을 교체
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA 클라이언트 사이드 라우팅: 정적 파일이 없으면 index.html로 폴백
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # 백엔드 API 요청을 greenops-backend 서비스로 프록시
    location /api/ {
        proxy_pass http://greenops-backend.greenops-backend.svc.cluster.local:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # 정적 에셋 캐시 (Vite 해시 파일명 활용)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 1단계에서 빌드된 dist 디렉토리를 nginx 서빙 경로로 복사
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# nginx는 포그라운드 실행 (daemon off)
CMD ["nginx", "-g", "daemon off;"]
