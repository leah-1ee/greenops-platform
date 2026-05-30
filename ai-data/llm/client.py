import os
from google import genai

def get_genai_client():
    """
    GEMINI_API_KEY 환경변수를 사용하여 google-genai 클라이언트를 반환합니다.
    키가 설정되지 않은 경우 KeyError를 발생시켜 비정상 종료되게 합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise KeyError(
            "환경변수 'GEMINI_API_KEY'가 설정되지 않았습니다. "
            "Gemini API 리포트 생성을 위해 터미널에 API 키 환경변수를 주입해야 합니다."
        )
    return genai.Client(api_key=api_key)


# === LOCAL_TEST_ONLY START ===
if __name__ == "__main__":
    try:
        client = get_genai_client()
        print("Gemini API Client 초기화 성공!")
    except KeyError as e:
        print(f"초기화 실패 (정상 동작 테스트): {e}")
# === LOCAL_TEST_ONLY END ===
