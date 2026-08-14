import json
from app.schemas.simulation import SimulationRequest

SYSTEM_PROMPT = """
당신은 여러 소비자 페르소나가 되어 제품과 광고 카피에 반응하는 역할극 시뮬레이터입니다.
주어진 각 페르소나의 입장에서 실제로 반응할 법한 내용을 작성하세요.

중요 규칙:
- 결과는 반드시 JSON만 반환하세요.
- 마크다운, 설명문, 코드블록을 넣지 마세요.
- 전달받은 모든 페르소나에 대해 각각 하나씩 반응을 작성하세요.
- 구매의향 점수는 1~10 사이 정수로 작성하세요. 모든 페르소나가 비슷한 점수를 받지 않도록, 페르소나 특성에 따라 실제로 점수가 갈리게 하세요.

페르소나 특성을 반응에 강하게 반영하세요:
- price_sensitivity가 높은 페르소나는 가격, 구독료, ROI(투자 대비 효과)를 가장 먼저 따지고 우려점에도 반영하세요.
- ai_familiarity가 낮은 페르소나는 AI 기능의 신뢰도나 사용 난이도 자체를 걱정하세요. ai_familiarity가 높으면 오히려 AI 기능의 디테일(정확도, 커스터마이징)을 따지세요.
- brand_sensitivity가 높은 페르소나는 후기, 검증된 사례, 브랜드 신뢰도를 중요하게 언급하세요.
- decision_style에 따라 반응 방식을 다르게 하세요: 즉흥형은 첫인상만으로 빠르게 결정하고, 분석형은 근거·수치·비교를 요구하고, 추천 의존형은 지인/후기 추천 여부를 중요하게 봅니다.
- past_failure_experience가 있는 페르소나는 그 경험을 구체적으로 언급하며 더 조심스럽고 방어적으로 반응하세요.
- current_solutions가 있는 페르소나는 반드시 기존 대안과 비교하는 관점에서 반응하세요.
- information_channels에 따라 어떤 근거(후기, 데이터, 지인 추천 등)를 신뢰하는지 반영하세요.
- reaction_type에 따라 말투와 판단 기준을 다르게 하세요 (예: skeptical=의심 많고 근거 요구, impulsive=즉흥적이고 감정적, rational=논리적이고 비교 중심, price_sensitive=가격 최우선, brand_loyal=기존에 쓰던 브랜드/서비스 선호, convenience_first=편의성 최우선, quality_first=품질/효과 최우선, novelty_seeker=새로움과 트렌드에 긍정적, risk_averse=리스크 회피, 보수적, pragmatic=실용적이고 균형잡힌 판단).
- 페르소나마다 문장 톤과 어휘를 다르게 하여 10명이 서로 다른 사람처럼 느껴지게 하세요.
"""


JSON_SCHEMA_HINT = """
{
  "responses": [
    {
      "persona_id": 1,
      "first_impression": "첫인상",
      "positive_points": ["장점1", "장점2"],
      "concerns": ["우려1", "우려2"],
      "purchase_intent_score": 7,
      "memorable_quote": "이 페르소나가 실제로 할 법한 인상적인 한마디",
      "suggested_improvement": "개선 제안"
    }
  ]
}
"""


def build_user_prompt(request: SimulationRequest, analysis: dict, personas: list) -> str:
    return f"""
다음 제품/광고에 대해 아래 페르소나들이 각각 어떻게 반응할지 시뮬레이션하세요.
각 페르소나의 price_sensitivity, ai_familiarity, brand_sensitivity, decision_style, past_failure_experience,
current_solutions, information_channels, reaction_type 필드를 반드시 반영해서 반응을 차별화하세요.

제품명: {request.product_name}
제품 설명: {request.product_description}
광고 카피: {request.ad_copy}

제품 분석 결과:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

페르소나 목록:
{json.dumps(personas, ensure_ascii=False, indent=2)}

아래 JSON 구조에 맞춰 반환하세요.
{JSON_SCHEMA_HINT}
"""
