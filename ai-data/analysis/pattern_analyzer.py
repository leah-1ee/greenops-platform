import os
import pandas as pd
from datetime import datetime
from carbon_aware.historical_client import get_historical_data

class PatternAnalyzer:
    def __init__(self, zone):
        self.zone = zone
        self.pattern_df = None
        self.overall_mean = 400.0  # fallback 기본값
        self._analyze()
        
    def _analyze(self):
        """과거 데이터를 분석하여 요일 및 시간대별 평균 탄소 집약도 테이블을 생성합니다."""
        data = get_historical_data(self.zone)
        if not data:
            print(f"[{self.zone}] 분석할 과거 데이터가 존재하지 않습니다. 기본 통계치를 사용합니다.")
            return
            
        df = pd.DataFrame(data)
        df["datetime"] = pd.to_datetime(df["datetime"])
        
        # 요일(weekday: 0=월요일, 6=일요일)과 시간(hour) 추출
        df["weekday"] = df["datetime"].dt.weekday
        df["hour"] = df["datetime"].dt.hour
        
        # 전체 평균 기록
        self.overall_mean = float(df["carbonIntensity"].mean())
        
        # 요일 및 시간대별 그룹 평균 계산
        grouped = df.groupby(["weekday", "hour"])["carbonIntensity"].mean().reset_index()
        self.pattern_df = grouped
        
    def predict_intensity(self, target_time):
        """
        특정 target_time (datetime 객체 또는 ISO 포맷 문자열)에 대한
        과거 평균 기반 탄소 집약도 추정값을 반환합니다.
        """
        if isinstance(target_time, str):
            try:
                target_time = pd.to_datetime(target_time)
            except Exception:
                return self.overall_mean
                
        if self.pattern_df is None or self.pattern_df.empty:
            return self.overall_mean
            
        weekday = target_time.weekday()
        hour = target_time.hour
        
        # 해당 요일 및 시간 매칭
        match = self.pattern_df[
            (self.pattern_df["weekday"] == weekday) & 
            (self.pattern_df["hour"] == hour)
        ]
        
        if not match.empty:
            return float(match.iloc[0]["carbonIntensity"])
            
        # 요일/시간 구체적 매칭 실패 시 시간대 평균으로 매칭 시도
        match_hour = self.pattern_df[self.pattern_df["hour"] == hour]
        if not match_hour.empty:
            return float(match_hour["carbonIntensity"].mean())
            
        return self.overall_mean


# === LOCAL_TEST_ONLY START ===
if __name__ == "__main__":
    # 테스트 구동
    analyzer = PatternAnalyzer("KR")
    print(f"전체 평균: {analyzer.overall_mean:.2f} gCO2/kWh")
    
    # 임의의 미래 시간 (예: 현재 시간 기준 추정)
    future_time = datetime.now()
    pred = analyzer.predict_intensity(future_time)
    print(f"추정 탄소 집약도 ({future_time}): {pred:.2f} gCO2/kWh")
# === LOCAL_TEST_ONLY END ===
