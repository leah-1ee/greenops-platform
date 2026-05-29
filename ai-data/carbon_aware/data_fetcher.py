
import os
import requests
import json
from datetime import datetime
import os
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)

token = os.environ["ELECTRICITYMAPS_TOKEN"]

zones = ["KR", "JP-TK", "US-MIDA-PJM"]

for zone in zones:

    url = f"https://api.electricitymap.org/v3/carbon-intensity/history?zone={zone}&disableEstimations=true"
    response = requests.get(url, headers={"auth-token": token})


    print(f"[{zone}] 상태코드: {response.status_code}")

    if response.status_code != 200:
        print(f"[{zone}] 건너뜀 (권한 없거나 에러)")
        continue

    # 5. 파일로 저장
    data = response.json()
    today = datetime.now().strftime("%Y%m%d")
    filename = os.path.join(DATA_DIR, f"{zone}_{today}.json")

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"저장됨: {filename}")