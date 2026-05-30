import os
import glob
import json
from datetime import datetime
from carbon_aware.preprocessor import preprocess_data

DATA_DIR = "/home/ubuntu/carbon-ai-data/data/raw/"

# 인메모리 캐시 저장소
# 구조: {(zone, today_str): cleaned_data}
_HISTORICAL_CACHE = {}

def get_historical_data(zone):
    """
    지정된 zone의 모든 이력 데이터를 로드하고 전처리하여 반환합니다.
    (인메모리 캐싱을 통해 대량의 파일 로드 시의 API 응답 지연을 방지합니다.)
    """
    today_str = datetime.now().strftime("%Y%m%d")
    cache_key = (zone, today_str)
    
    # 캐시 히트 검사
    if cache_key in _HISTORICAL_CACHE:
        return _HISTORICAL_CACHE[cache_key]

    # === LOCAL_TEST_ONLY START ===
    # 리눅스 배포 환경의 절대 경로를 유지하되, 로컬 개발을 위해 fallback을 지정합니다.
    data_dir = DATA_DIR
    if not os.path.exists(data_dir):
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
    # === LOCAL_TEST_ONLY END ===
    # 프로덕션 코드에서는 아래 라인만 남기면 됩니다:
    # data_dir = DATA_DIR
        
    files = glob.glob(os.path.join(data_dir, f"{zone}_*.json"))
    if not files:
        return []
        
    all_history = []
    for f in sorted(files):
        try:
            with open(f, "r") as file:
                raw = json.load(file)
            cleaned = preprocess_data(raw)
            all_history.extend(cleaned)
        except Exception as e:
            print(f"이력 데이터 로딩 에러 ({f}): {e}")
            
    # 중복 제거 및 시간 순 정렬
    seen = set()
    unique_history = []
    for item in all_history:
        if item["datetime"] not in seen:
            seen.add(item["datetime"])
            unique_history.append(item)
            
    unique_history.sort(key=lambda x: x["datetime"])
    
    # 메모리 캐시에 적재
    _HISTORICAL_CACHE[cache_key] = unique_history
    return unique_history


# === LOCAL_TEST_ONLY START ===
if __name__ == "__main__":
    import time
    # 캐싱 속도 검증 테스트
    print("--- 캐시 성능 테스트 ---")
    start_time = time.time()
    data1 = get_historical_data("KR")
    load_time1 = time.time() - start_time
    print(f"1차 로드 완료 (디스크 읽기): {load_time1:.6f}초 (데이터 개수: {len(data1)})")
    
    start_time = time.time()
    data2 = get_historical_data("KR")
    load_time2 = time.time() - start_time
    print(f"2차 로드 완료 (캐시 히트): {load_time2:.6f}초 (데이터 개수: {len(data2)})")
    
    if load_time1 > 0:
        improvement = (load_time1 - load_time2) / load_time1 * 100
        print(f"성능 개선 비율: {improvement:.2f}%")
# === LOCAL_TEST_ONLY END ===
