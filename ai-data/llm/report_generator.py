import os
import json
import glob
import pandas as pd
from google import genai
from analysis.optimizer import find_optimal_window

DATA_DIR = "/home/ubuntu/carbon-ai-data/data/raw/"
WORK_HOURS = 3
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
    opt = find_optimal_window(df, WORK_HOURS)
    results.append({
        "zone": zone,
        "avg": round(avg, 1),
        "opt_time": str(opt["start_time"]),
        "opt_intensity": opt["avg_intensity"]
    })

best = min(results, key=lambda x: x["opt_intensity"])

regions_summary = "\n".join([
    f"- {r['zone']}: 평균 {r['avg']} gCO2/kWh | 최적 시간 {r['opt_time']} ({r['opt_intensity']} gCO2/kWh)"
    for r in results
])

prompt = f"""
당신은 탄소 인식 클라우드 컴퓨팅 전문가입니다.
다음 멀티리전 탄소 분석 결과를 바탕으로 한국어로 추천 리포트를 한 문단으로 작성하세요.

분석 리전:
{regions_summary}

최적 리전: {best['zone']} ({best['opt_intensity']} gCO2/kWh)
작업 시간: {WORK_HOURS}시간

최적 리전과 시간, 다른 리전 대비 장점, 절감 효과를 포함하세요.
"""

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)
print(response.text)