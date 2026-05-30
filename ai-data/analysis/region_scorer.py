import json
import os
import pandas as pd
from analysis.optimizer import find_optimal_window_future
from analysis.pattern_analyzer import PatternAnalyzer

def get_best_region(work_hours=3, zones=None):
    """
    각 리전의 과거 데이터 패턴 분석기(PatternAnalyzer)를 활용하여
    미래 24시간 내에서 최적의 실행 시간대와 리전을 도출합니다.
    형식이나 API 명세(JSON 반환 키 구조 등)는 백엔드와 상의된 기존 스펙을 유지합니다.
    """
    if zones is None:
        zones = ["KR", "JP-TK", "US-MIDA-PJM"]
    results = []

    for zone in zones:
        try:
            # PatternAnalyzer 초기화 (내부적으로 historical_client를 통해 데이터 자동 로드 및 분석)
            analyzer = PatternAnalyzer(zone)
            
            # 전체 평균
            avg = analyzer.overall_mean
            
            # 향후 24시간 중 최적 실행 시간대 도출
            opt = find_optimal_window_future(analyzer, work_hours)
            
            results.append({
                "zone": zone,
                "avg": round(avg, 1),
                "opt_time": str(opt["start_time"]),
                "opt_intensity": opt["avg_intensity"]
            })
        except Exception as e:
            print(f"[{zone}] 리전 스코어링 실패: {e}")
            continue

    if not results:
        return None

    # 최적 리전은 예상 탄소 집약도가 가장 낮은 곳으로 선정
    best = min(results, key=lambda x: x["opt_intensity"])
    return {
        "best_zone": best["zone"],
        "opt_time": best["opt_time"],
        "opt_intensity": best["opt_intensity"],
        "all_zones": results
    }


# === LOCAL_TEST_ONLY START ===
if __name__ == "__main__":
    result = get_best_region(3)
    if result:
        print(f"최적 리전: {result['best_zone']}")
        print(f"최적 시작: {result['opt_time']}")
        print(f"탄소 집약도: {result['opt_intensity']} gCO2/kWh")
        print("상세 리전별 데이터:")
        for r in result["all_zones"]:
            print(f"  - [{r['zone']}] 평균: {r['avg']}, 최적시간: {r['opt_time']}, 최적배출량: {r['opt_intensity']}")
# === LOCAL_TEST_ONLY END ===