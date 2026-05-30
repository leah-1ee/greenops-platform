import json
import os
import glob

def preprocess_data(raw_data):
    """
    원시 데이터(dict)를 받아서 결측치를 제외하고 시간순으로 정렬된 데이터를 반환합니다.
    백엔드와 합의된 형식: [{"datetime": "...", "carbonIntensity": ...}, ...]
    """
    cleaned = []
    if not raw_data or "history" not in raw_data:
        return cleaned
        
    for item in raw_data["history"]:
        if item.get("carbonIntensity") is None:   # 값 없으면 건너뜀
            continue
        cleaned.append({
            "datetime": item["datetime"],
            "carbonIntensity": item["carbonIntensity"]
        })
    
    cleaned.sort(key=lambda x: x["datetime"])
    return cleaned

def preprocess_file(filepath):
    """
    파일 경로를 받아서 전처리를 수행하고 결과를 반환합니다.
    """
    try:
        with open(filepath, "r") as f:
            raw = json.load(f)
        return preprocess_data(raw)
    except Exception as e:
        print(f"전처리 에러 ({filepath}): {e}")
        return []


# === LOCAL_TEST_ONLY START ===
if __name__ == "__main__":
    # 기존 테스트 코드와 호환성 유지
    # 만약 기존 파일이 없다면 최신 파일이나 mock으로 생성된 임의의 파일 사용
    test_file = "data/raw/KR_20260524.json"
    if not os.path.exists(test_file):
        raw_files = glob.glob("data/raw/*.json")
        if raw_files:
            test_file = raw_files[0]
            
    print(f"테스트 파일 전처리 진행: {test_file}")
    if os.path.exists(test_file):
        cleaned = preprocess_file(test_file)
        print(f"총 {len(cleaned)}개")
        print(cleaned[:3])
    else:
        print("테스트용 raw json 파일이 존재하지 않습니다.")
# === LOCAL_TEST_ONLY END ===