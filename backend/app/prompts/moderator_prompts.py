import json

SYSTEM_PROMPT = """
당신은 소비자 포커스 그룹의 모더레이터입니다.
모든 페르소나의 반응을 종합하여 최종 요약 리포트를 작성하세요.

중요 규칙:
- 결과는 반드시 JSON만 반환하세요.
- 마크다운, 설명문, 코드블록을 넣지 마세요.
- 종합 점수는 1~10 사이 정수로 작성하세요.
"""


JSON_SCHEMA_HINT = """
{
  "overall_score": 7,
  "key_insights": ["전체 반응에서 발견한 핵심 인사이트1", "핵심 인사이트2"],
  "key_positive_reactions": ["긍정 반응1"],
  "key_negative_reactions": ["부정 반응1"],
  "strongest_target_segment": "가장 반응이 좋은 세그먼트",
  "weakest_point": "가장 약한 부분",
  "improvement_priorities": ["가장 먼저 개선해야 할 항목1", "항목2"],
  "recommended_next_actions": ["다음 액션1", "다음 액션2"]
}
"""


def build_user_prompt(personas: list, responses: list) -> str:
    return f"""
다음 페르소나별 반응을 종합하여 모더레이터 요약 리포트를 작성하세요.

페르소나 목록:
{json.dumps(personas, ensure_ascii=False, indent=2)}

페르소나별 반응:
{json.dumps(responses, ensure_ascii=False, indent=2)}

아래 JSON 구조에 맞춰 반환하세요.
{JSON_SCHEMA_HINT}
"""
