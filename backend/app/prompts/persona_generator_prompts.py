import json
from app.schemas.simulation import SimulationRequest

SYSTEM_PROMPT = """
당신은 소비자 조사 전문가입니다.
제품 분석 결과와 타겟 고객 정보를 참고하여 실제 사람처럼 입체적인 소비자 페르소나를 생성하세요.

중요 규칙:
- 결과는 반드시 JSON만 반환하세요.
- 마크다운, 설명문, 코드블록을 넣지 마세요.
- 페르소나는 반드시 10명 생성하세요.

다양성 규칙 (반드시 지킬 것):
- 10명의 말투, 고민, 반응이 서로 겹치지 않게 하세요. 같은 문장 패턴을 반복하지 마세요.
- 나이대, 소득 수준, 라이프스타일, AI 친숙도, 가격 민감도, 브랜드 민감도, 구매 결정 방식(decision_style)을 10명 모두 다르게 구성하세요.
- 타겟 고객과 완전히 동떨어지면 안 되지만, 다음을 반드시 섞으세요:
  - 타겟에 정확히 부합하는 사람 3~4명
  - 타겟과 약간 거리가 있거나 회의적인 사람 2~3명
  - 타겟이 아니거나 전환이 어려운 사람 1~2명
- 구매 가능성이 높은 사람, 중립적인 사람, 낮은 사람이 골고루 섞이도록 하세요. 10명 모두 우호적이면 안 됩니다.
- reaction_type은 아래 목록에서 골고루 분산해서 사용하세요 (10명이 3종류 이하로 몰리지 않게 하세요):
  skeptical, impulsive, rational, price_sensitive, brand_loyal, convenience_first, quality_first, novelty_seeker, risk_averse, pragmatic
- past_failure_experience는 모든 사람에게 억지로 채우지 말고, 실제로 있을 법한 사람만 구체적으로 채우고 없으면 빈 문자열로 두세요.
- current_solutions, frequently_used_apps, information_channels은 각 페르소나의 라이프스타일과 연령대에 맞게 현실적으로 작성하세요.
"""


JSON_SCHEMA_HINT = """
{
  "personas": [
    {
      "id": 1,
      "name": "페르소나 이름",
      "age": 32,
      "gender": "여성",
      "job": "직업",
      "income_level": "중간",
      "personality": "신중하고 가격에 민감함 (소비성향)",
      "pain_point": "현재 겪고 있는 주요 고민",
      "purchase_barrier": "구매를 망설이게 만드는 요인",
      "region": "거주 지역 (예: 서울/수도권, 지방 광역시 등)",
      "marital_status": "미혼 / 기혼 등",
      "has_children": false,
      "lifestyle": "일상 패턴과 라이프스타일을 한두 문장으로",
      "ai_familiarity": "낮음 / 중간 / 높음 중 하나",
      "brand_sensitivity": "낮음 / 중간 / 높음 중 하나",
      "price_sensitivity": "낮음 / 중간 / 높음 중 하나",
      "current_solutions": ["현재 사용 중인 대안이나 방법"],
      "decision_style": "즉흥형 / 분석형 / 추천 의존형 등 구매 의사결정 방식",
      "frequently_used_apps": ["자주 쓰는 앱이나 서비스"],
      "information_channels": ["제품 정보를 얻는 채널 (예: 유튜브 리뷰, 지인 추천, 블로그)"],
      "past_failure_experience": "과거 유사 제품/서비스에서 겪은 실패 경험 (없으면 빈 문자열)",
      "reaction_type": "skeptical / impulsive / rational / price_sensitive / brand_loyal / convenience_first / quality_first / novelty_seeker / risk_averse / pragmatic 중 하나"
    }
  ]
}
"""


def build_user_prompt(request: SimulationRequest, analysis: dict) -> str:
    return f"""
다음 제품 분석 결과와 타겟 고객을 참고하여 소비자 페르소나 10명을 생성하세요.

제품명: {request.product_name}
타겟 고객: {request.target_audience}

제품 분석 결과:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

아래 JSON 구조에 맞춰 반환하세요. 필드는 하나도 빠짐없이 채우세요.
{JSON_SCHEMA_HINT}
"""
