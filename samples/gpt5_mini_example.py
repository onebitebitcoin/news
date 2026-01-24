"""
GPT-5-mini Response API 예시
OpenAI의 새로운 Responses API를 사용하여 GPT-5-mini 모델 호출

참고 자료:
- OpenAI GPT-5-mini 문서: https://platform.openai.com/docs/models/gpt-5-mini
- OpenAI Developer Quickstart: https://platform.openai.com/docs/quickstart
- OpenAI Cookbook - GPT-5 예시: https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools
"""

from openai import OpenAI

# ============================================
# API 키 설정 (여기에 직접 입력)
# ============================================
OPENAI_API_KEY = "sk-your-api-key-here"


def main():
    client = OpenAI(api_key=OPENAI_API_KEY)

    # 기본 호출
    print("=== 기본 호출 ===")
    response = client.responses.create(
        model="gpt-5-mini",
        input="안녕하세요, 간단한 인사를 해주세요."
    )
    print(response.output_text)
    print()

    # verbosity 파라미터 사용
    print("=== verbosity 파라미터 사용 ===")
    response = client.responses.create(
        model="gpt-5-mini",
        input="Python의 장점을 설명해주세요.",
        text={"verbosity": "low"}
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
