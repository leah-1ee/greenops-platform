import json
import pandas as pd

def find_optimal_window(df, window_hours):
    """N시간 작업의 최적 시작 시간을 찾는 함수"""
    df = df.sort_values("datetime").reset_index(drop=True)
    df["rolling_avg"] = df["carbonIntensity"].rolling(window_hours).mean()
    best_end = df["rolling_avg"].idxmin()
    best_start = best_end - (window_hours - 1)
    return {
        "start_time": df.loc[best_start, "datetime"],
        "avg_intensity": round(df.loc[best_end, "rolling_avg"], 1)
    }


# ↓ 이 파일을 '직접' 실행할 때만 돌아감 (import 시엔 안 돌아감)
if __name__ == "__main__":
    with open("/home/ubuntu/carbon-ai-data/data/raw/KR_20260524.json") as f:
        raw = json.load(f)
    df = pd.DataFrame(raw["history"])
    df["datetime"] = pd.to_datetime(df["datetime"])

    best = df.loc[df["carbonIntensity"].idxmin()]
    avg = df["carbonIntensity"].mean()
    saving = (avg - best["carbonIntensity"]) / avg * 100
    print(f"✅ 가장 깨끗한 시간: {best['datetime']} ({best['carbonIntensity']})")
    print(f"📊 평균 대비 절감률: {saving:.1f}%")

    for hours in [1, 3, 5]:
        result = find_optimal_window(df, hours)
        print(f"⏰ {hours}시간 → {result['start_time']} ({result['avg_intensity']})")