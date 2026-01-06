"""gpt_judge.py

OpenAI Chat Completions를 호출해서 "마크업 오류 방지" 기준 위반 여부를 JSON으로 판단.
- API 키는 환경변수 OPENAI_API_KEY 우선
- 없으면 config.json(로컬 저장)에서 로드

주의: 이 코드는 openai>=1.x ("from openai import OpenAI") 기준입니다.
"""

from __future__ import annotations

from openai import OpenAI

from prompt import SYSTEM_PROMPT
from config import load_api_key, DEFAULT_MODEL


def judge_markup(gpt_input: str) -> str:
    api_key = load_api_key()
    if not api_key:
        # main.py에서 그대로 출력되도록 문자열로 반환
        return "❌ OPENAI_API_KEY가 설정되지 않았습니다. (상단 'API 키 설정'에서 등록해주세요)"

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": gpt_input},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    return content or ""
