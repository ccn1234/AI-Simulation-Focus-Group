from app.schemas.simulation import SimulationRequest

SYSTEM_PROMPT = """
당신은 시니어 프로덕트 마케팅 분석가입니다.
사용자가 입력한 제품 설명과 광고 카피를 분석하세요.

중요 규칙:
- 결과는 반드시 JSON만 반환하세요.
- 마크다운, 설명문, 코드블록을 넣지 마세요.
"""


JSON_SCHEMA_HINT = """
{
  "core_value_proposition": "제품의 핵심 가치제안 한두 문장",
  "expected_purchase_motivations": ["예상 구매동기1", "예상 구매동기2"],
  "expected_resistance_factors": ["예상 구매 저항요소1", "예상 구매 저항요소2"],
  "main_competitors_or_alternatives": ["소비자가 떠올릴 만한 비교 대상1", "비교 대상2"],
  "copy_strengths": ["광고 카피의 강점1", "강점2"],
  "copy_weaknesses": ["광고 카피의 약점1", "약점2"],
  "target_fit_summary": "타겟 고객과 제품/카피의 적합도에 대한 한두 문장 요약"
}
"""


def build_user_prompt(request: SimulationRequest) -> str:
    return f"""
다음 제품/광고를 분석하세요.

제품명: {request.product_name}
제품 설명: {request.product_description}
타겟 고객: {request.target_audience}
광고 카피: {request.ad_copy}

아래 JSON 구조에 맞춰 반환하세요.
{JSON_SCHEMA_HINT}
"""
