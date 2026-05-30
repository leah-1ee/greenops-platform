import json
import os
import pandas as pd
from datetime import datetime, timedelta
from analysis.pattern_analyzer import PatternAnalyzer

def find_optimal_window(df, window_hours):
    """N시간 작업의 최적 시작 시간을 찾는 함수"""
    df = df.sort_values("datetime").reset_index(drop=True)
    df["rolling_avg"] = df["carbonIntensity"].rolling(window_hours).mean()
    best_end = df["rolling_avg"].idxmin()
    best_start = best_end - (window_hours - 1)
    
    # datetime 타입에 따른 안전한 문자열 변환
    start_dt = df.loc[best_start, "datetime"]
    if isinstance(start_dt, pd.Timestamp):
        start_dt_str = start_dt.strftime("%Y-%m-%dT%H:00:00.000Z")
    else:
        start_dt_str = str(start_dt)
        
    return {
        "start_time": start_dt_str,
        "avg_intensity": round(df.loc[best_end, "rolling_avg"], 1)
    }

def find_optimal_window_future(analyzer: PatternAnalyzer, window_hours, start_from=None):
    """
    미래 특정 시점(기본은 현재)부터 향후 24시간 범위 내에서,
    PatternAnalyzer를 이용해 추정한 탄소 집약도 기준 N시간 작업의 최적 시작 시간윈도우를 반환합니다.
    """
    if start_from is None:
        start_from = datetime.now()
        
    # 향후 24시간 동안의 예상 타임라인 구성 (시간 단위)
    future_times = [start_from + timedelta(hours=i) for i in range(24)]
    
    # 각 시간별 예상 탄소 집약도 조회
    data = []
    for dt in future_times:
        pred_val = analyzer.predict_intensity(dt)
        data.append({
            "datetime": dt,
            "carbonIntensity": pred_val
        })
        
    df = pd.DataFrame(data)
    return find_optimal_window(df, window_hours)


# === LOCAL_TEST_ONLY START ===
if __name__ == "__main__":
    # 리눅스 배포 경로를 사용하되 로컬 테스트를 위해 fallback 처리
    raw_path = "/home/ubuntu/carbon-ai-data/data/raw/KR_20260524.json"
    if not os.path.exists(raw_path):
        import glob
        raw_files = glob.glob("../data/raw/KR_*.json")
        if raw_files:
            raw_path = raw_files[0]
            
    if os.path.exists(raw_path):
        with open(raw_path) as f:
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
            
        # PatternAnalyzer 미래 연동 테스트
        print("\n--- PatternAnalyzer 미래 예측 최적화 테스트 ---")
        analyzer = PatternAnalyzer("KR")
        for hours in [1, 3, 5]:
            result = find_optimal_window_future(analyzer, hours)
            print(f"⏰ 미래 {hours}시간 최적윈도우 → {result['start_time']} ({result['avg_intensity']})")
    else:
        print("테스트용 파일이 없어 통계 최적화 테스트를 건너뜁니다.")
# === LOCAL_TEST_ONLY END ===