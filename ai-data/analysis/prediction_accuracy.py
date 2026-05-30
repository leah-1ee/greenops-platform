import os
import pandas as pd
import numpy as np
from datetime import datetime
from carbon_aware.historical_client import get_historical_data
from analysis.pattern_analyzer import PatternAnalyzer

def calculate_mae(zone):
    """
    특정 zone의 이력 데이터를 불러와 학습/검증 데이터로 분할 후
    통계 모델(PatternAnalyzer)의 예측 정확도(MAE 및 오차율)를 계산합니다.
    """
    data = get_historical_data(zone)
    if not data or len(data) < 12:
        return {
            "zone": zone,
            "error": "분석을 위한 충분한 이력 데이터가 존재하지 않습니다."
        }
        
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["datetime"])
    
    # 시간 순 정렬
    df = df.sort_values("datetime").reset_index(drop=True)
    
    # Train / Test 분할 (마지막 24개 데이터, 즉 최근 하루치를 테스트 셋으로 떼어둠)
    # 데이터 총량이 24개 이하라면 8:2 비율로 나눔
    if len(df) <= 24:
        split_idx = int(len(df) * 0.8)
    else:
        split_idx = len(df) - 24
        
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    # 훈련용 데이터 기반으로 통계 평균값 추출
    train_df = train_df.copy()
    train_df["weekday"] = train_df["datetime"].dt.weekday
    train_df["hour"] = train_df["datetime"].dt.hour
    
    overall_mean = float(train_df["carbonIntensity"].mean())
    grouped = train_df.groupby(["weekday", "hour"])["carbonIntensity"].mean().reset_index()
    
    # 테스트 셋 평가
    actuals = []
    predictions = []
    
    for idx, row in test_df.iterrows():
        dt = row["datetime"]
        actual = row["carbonIntensity"]
        
        # weekday, hour 매칭
        match = grouped[(grouped["weekday"] == dt.weekday()) & (grouped["hour"] == dt.hour)]
        if not match.empty:
            pred = float(match.iloc[0]["carbonIntensity"])
        else:
            # 시간대만 매칭
            match_hour = grouped[grouped["hour"] == dt.hour]
            if not match_hour.empty:
                pred = float(match_hour["carbonIntensity"].mean())
            else:
                pred = overall_mean
                
        actuals.append(actual)
        predictions.append(pred)
        
    actuals = np.array(actuals)
    predictions = np.array(predictions)
    
    # MAE (Mean Absolute Error) 계산
    mae = np.mean(np.abs(actuals - predictions))
    
    # 상대 오차율 (%) 계산
    mean_actual = np.mean(actuals)
    error_rate = (mae / mean_actual * 100) if mean_actual > 0 else 0.0
    
    return {
        "zone": zone,
        "total_count": len(df),
        "train_count": len(train_df),
        "test_count": len(test_df),
        "actual_mean": round(float(mean_actual), 2),
        "mae": round(float(mae), 2),
        "error_rate_pct": round(float(error_rate), 2)
    }


# === LOCAL_TEST_ONLY START ===
if __name__ == "__main__":
    print("--- 통계 모델 예측 오차(MAE) 분석 ---")
    zones = ["KR", "JP-TK", "US-MIDA-PJM"]
    for zone in zones:
        res = calculate_mae(zone)
        print(f"\n 리전: {res['zone']}")
        if "error" in res:
            print(f"  실패 사유: {res['error']}")
        else:
            print(f"  전체 데이터 수: {res['total_count']}개 (훈련: {res['train_count']}, 테스트: {res['test_count']})")
            print(f"  실제 평균 집약도: {res['actual_mean']} gCO2/kWh")
            print(f"  평균 절대 오차 (MAE): {res['mae']} gCO2/kWh")
            print(f"  상대 오차율: {res['error_rate_pct']}%")
# === LOCAL_TEST_ONLY END ===
