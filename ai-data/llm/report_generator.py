import os
from llm.client import get_genai_client
from llm.prompt_templates import get_recommendation_report_prompt
from analysis.region_scorer import get_best_region

def generate_carbon_report(work_hours=3, zones=None):
    """
    지정된 zones 및 작업 시간에 대해 최적 리전을 스코어링하고
    그 결과를 기반으로 Gemini API를 호출하여 자연어 리포트를 생성해 반환합니다.
    """
    # 1. 최적 리전 및 데이터 추출
    scoring_result = get_best_region(work_hours=work_hours, zones=zones)
    if not scoring_result:
        return "분석 가능한 이력 탄소 배출 데이터가 부족하여 리포트를 생성할 수 없습니다."
        
    # 2. Gemini 클라이언트 가져오기 (환경변수 부족 시 KeyError 발생)
    client = get_genai_client()
    
    # 3. 프롬프트 구성
    prompt = get_recommendation_report_prompt(scoring_result, work_hours)
    
    # 4. Gemini 모델 호출 (gemini-2.5-flash 모델 적용)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API 호출 중 오류 발생: {e}")
        raise e


# === LOCAL_TEST_ONLY START ===
if __name__ == "__main__":
    # 이 파일 단독 실행 테스트 (터미널에 GEMINI_API_KEY가 반드시 설정되어 있어야 함)
    # 윈도우 파워쉘 실행 예: $env:GEMINI_API_KEY="your-key-here"; python -m llm.report_generator
    print("--- 자연어 리포트 생성기 테스트 ---")
    try:
        report = generate_carbon_report(work_hours=3)
        print("\n[생성된 리포트 내용]")
        print(report)
    except Exception as e:
        print(f"\n[오류 발생] 리포트 생성 실패: {e}")
# === LOCAL_TEST_ONLY END ===