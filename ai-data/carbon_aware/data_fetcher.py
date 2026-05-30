import os
import sys
import requests
import json
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)

# === LOCAL_TEST_ONLY START ===
# argument 또는 환경변수로 mock mode 체크
is_mock_mode = "--mock" in sys.argv or os.environ.get("MOCK_MODE") == "true"
# === LOCAL_TEST_ONLY END ===

zones = ["KR", "JP-TK", "US-MIDA-PJM"]
today = datetime.now().strftime("%Y%m%d")

# === LOCAL_TEST_ONLY START ===
if is_mock_mode:
    print("[MOCK] MOCK MODE 활성화: 모의 탄소 집약도 데이터를 생성합니다.")
    for zone in zones:
        history = []
        # 최근 24시간 동안의 모의 데이터 생성
        base_time = datetime.now() - timedelta(days=1)
        # 리전별 탄소 집약도 기본값 설정
        base_intensity = {"KR": 450, "JP-TK": 380, "US-MIDA-PJM": 320}.get(zone, 400)
        
        for hour in range(24):
            dt = base_time + timedelta(hours=hour)
            # 시간대에 따른 임의의 변동폭 추가 (낮 시간 감소, 밤 시간 증가 등)
            variation = int(50 * (random.random() - 0.5))
            intensity = max(50, base_intensity + variation)
            history.append({
                "datetime": dt.strftime("%Y-%m-%dT%H:00:00.000Z"),
                "carbonIntensity": intensity,
                "isEstimated": False
            })
            
        data = {"history": history}
        filename = os.path.join(DATA_DIR, f"{zone}_{today}.json")
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[MOCK] 저장됨: {filename}")
# === LOCAL_TEST_ONLY END ===
else:
    # 프로덕션 실행: 토큰이 반드시 필요
    token = os.environ.get("ELECTRICITYMAPS_TOKEN")
    if not token:
        raise KeyError(
            "환경변수 'ELECTRICITYMAPS_TOKEN'이 설정되지 않았습니다. "
            "실제 실행을 위해서는 토큰이 필수적입니다. 로컬 테스트를 원하시면 "
            "터미널에서 MOCK_MODE=true를 설정하거나 '--mock' 인자를 전달하여 실행하십시오."
        )
        
    for zone in zones:
        url = f"https://api.electricitymap.org/v3/carbon-intensity/history?zone={zone}&disableEstimations=true"
        response = requests.get(url, headers={"auth-token": token})

        print(f"[{zone}] 상태코드: {response.status_code}")

        if response.status_code != 200:
            print(f"[{zone}] 건너뜀 (권한 없거나 에러)")
            continue

        data = response.json()
        filename = os.path.join(DATA_DIR, f"{zone}_{today}.json")

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"저장됨: {filename}")