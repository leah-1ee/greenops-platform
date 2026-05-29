import os
import requests

TOKEN = os.environ["ELECTRICITYMAPS_TOKEN"]

def get_current_intensity(zone):
    """지금 이 순간의 탄소 집약도 조회"""
    url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone}"
    response = requests.get(url, headers={"auth-token": TOKEN})

    if response.status_code != 200:
        return None

    data = response.json()
    return {
        "zone": zone,
        "carbonIntensity": data.get("carbonIntensity"),
        "datetime": data.get("datetime"),
        "isEstimated": data.get("isEstimated")
    }


if __name__ == "__main__":
    zones = ["KR", "JP-TK", "US-MIDA-PJM"]
    for zone in zones:
        result = get_current_intensity(zone)
        if result:
            print(f"[{zone}] 현재: {result['carbonIntensity']} gCO2/kWh ({result['datetime']})")
        else:
            print(f"[{zone}] 데이터 없음")