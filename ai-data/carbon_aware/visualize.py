import json
import pandas as pd
import matplotlib.pyplot as plt

# 1. 데이터 읽기 (본인 파일명으로!)
with open("data/raw/KR_20260524.json", "r") as f:
    raw = json.load(f)

# 2. 표(DataFrame)로 만들기
df = pd.DataFrame(raw["history"])
df = df[["datetime", "carbonIntensity"]]
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime")

# 3. 그래프 그려서 파일로 저장
plt.figure(figsize=(12, 5))
plt.plot(df["datetime"], df["carbonIntensity"], marker="o")
plt.title("KR Carbon Intensity (24h)")
plt.xlabel("Time")
plt.ylabel("gCO2/kWh")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("data/KR_intensity.png")

print("그래프 저장됨: data/KR_intensity.png")