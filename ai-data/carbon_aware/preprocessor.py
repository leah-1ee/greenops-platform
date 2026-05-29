import json

# 1. 저장된 파일 읽기 (본인 파일명으로!)
with open("data/raw/KR_20260524.json", "r") as f:
    raw = json.load(f)

# 2. 필요한 것만 뽑기 + 결측치 건너뛰기
cleaned = []
for item in raw["history"]:
    if item["carbonIntensity"] is None:   # 값 없으면 건너뜀
        continue
    cleaned.append({
        "datetime": item["datetime"],
        "carbonIntensity": item["carbonIntensity"]
    })

# 3. 시간순 정렬
cleaned.sort(key=lambda x: x["datetime"])

# 4. 결과 확인
print(f"총 {len(cleaned)}개")
print(cleaned[:3])