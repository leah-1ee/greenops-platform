import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = """
당신은 탄소 인식 클라우드 컴퓨팅 전문가입니다.

다음 데이터를 기반으로 사용자에게 추천을 한국어로 한 문단으로 작성해주세요:

- 최적 리전: koreacentral (한국)
- 현재 탄소 집약도: 450 gCO2/kWh
- 24시간 평균: 480 gCO2/kWh
- 추천 실행 시간: 새벽 3시 (가장 낮은 집약도)
- 예상 절감량: 기준 대비 12%
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)
