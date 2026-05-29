import json
import glob
import pandas as pd
import os
from analysis.optimizer import find_optimal_window

DATA_DIR = "/home/ubuntu/carbon-ai-data/data/raw/"

def get_best_region(work_hours=3, zones = None):
    """멀티리전 비교 → 최적 리전 반환"""
    if zones is None : 
        zones = ["KR", "JP-TK", "US-MIDA-PJM"]
    results = []

    for zone in zones:
        files = glob.glob(f"{DATA_DIR}{zone}_*.json")
        if not files:
            continue
        filepath = None
        for f in sorted(files, reverse=True):
            data = json.load(open(f))
            if data.get("history"):
                filepath = f
                break
        if not filepath:
            continue
        with open(filepath) as f:
            raw = json.load(f)
        df = pd.DataFrame(raw["history"])
        if df.empty or "datetime" not in df.columns:
            continue
        df["datetime"] = pd.to_datetime(df["datetime"])
        avg = df["carbonIntensity"].mean()
        opt = find_optimal_window(df, work_hours)
        results.append({
            "zone": zone,
            "avg": round(avg, 1),
            "opt_time": str(opt["start_time"]),
            "opt_intensity": opt["avg_intensity"]
        })

    if not results:
        return None

    best = min(results, key=lambda x: x["opt_intensity"])
    return {
        "best_zone": best["zone"],
        "opt_time": best["opt_time"],
        "opt_intensity": best["opt_intensity"],
        "all_zones": results
    }


if __name__ == "__main__":
    result = get_best_region(3)
    if result:
        print(f"🌍 최적 리전: {result['best_zone']}")
        print(f"⏰ 최적 시작: {result['opt_time']}")
        print(f"🌱 탄소 집약도: {result['opt_intensity']} gCO2/kWh")