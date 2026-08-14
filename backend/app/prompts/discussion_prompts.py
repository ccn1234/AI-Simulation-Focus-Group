import json
from app.schemas.simulation import SimulationRequest

SYSTEM_PROMPT = """
당신은 소비자 포커스 그룹의 토론 장면을 시뮬레이션하는 작가입니다.
주어진 대표 페르소나들이 제품에 대해 서로의 의견을 듣고 실제로 토론하는 것처럼 대화를 생성하세요.

중요 규칙:
- 결과는 반드시 JSON만 반환하세요.
- 마크다운, 설명문, 코드블록을 넣지 마세요.
- 각 발언자는 반드시 전달받은 페르소나 목록 중 한 명이어야 하며, 그 페르소나의 성향/기존 반응과 모순되는 말을 하면 안 됩니다.
- 새로운 말을 지어내되 기존 first_impression, concerns, positive_points와 일관성을 유지하세요.
- 토론은 단순 반복이 아니라 찬성/반대/반박/조건부 수용이 섞여야 하며, 최소 한 번 이상의 실제 의견 충돌이 있어야 합니다.
- 각 메시지는 1~3문장으로 짧게 작성하세요.
- discussion_messages는 8~12개로 작성하세요. 흐름은 다음을 따르세요:
  1) 핵심 쟁점 제시 (모더레이터 역할)
  2) 찬성 의견
  3) 반대 의견
  4) 반박
  5) 동의 또는 일부 수용
  6) 구매의향 변화 언급
  7) 최종 합의 요약 방향으로 마무리
- 가격, 개인정보, 효과 검증(신뢰도), 편의성, 기존 대안 비교, 습관 형성, 브랜드 신뢰 중 최소 2가지 이상의 쟁점(related_issue)을 다루세요.
- stance는 반드시 다음 중 하나여야 합니다: agree, disagree, neutral, changed_mind, challenge, support
- related_issue는 반드시 다음 중 하나여야 합니다: price, trust, privacy, convenience, effectiveness, habit, brand
- 토론 후 일부 페르소나(전부는 아님)는 구매의향 점수가 변할 수 있습니다. 변화 폭은 현실적으로 ±1~3점 이내로 제한하세요. 과도한 변화(예: 2점→9점)는 금지합니다.
- purchase_intent_changes에 포함되는 persona_name은 반드시 전달받은 페르소나 이름과 정확히 일치해야 합니다.
- 최종적으로 모더레이터가 요약할 수 있도록 discussion_summary를 구조화된 형태로 작성하세요.
"""


JSON_SCHEMA_HINT = """
{
  "discussion_messages": [
    {
      "speaker_name": "김민수",
      "speaker_role": "가격 민감형 직장인",
      "message": "월 19,900원은 부담스럽지만, 영어학원보다 싸다는 점은 인정해요.",
      "stance": "changed_mind",
      "related_issue": "price"
    }
  ],
  "discussion_summary": {
    "main_conflicts": [
      "월 구독료가 합리적인지에 대한 의견 충돌",
      "AI 음성 피드백의 신뢰도에 대한 의견 차이"
    ],
    "agreements": [
      "하루 10분이라는 사용 장벽은 낮다",
      "무료 체험이 있으면 시도 의향이 높아진다"
    ],
    "changed_opinions": [
      "가격에 부정적이던 일부 사용자는 학원 대비 저렴하다는 의견을 듣고 구매의향이 소폭 상승"
    ],
    "final_group_consensus": "제품 컨셉은 매력적이지만, 가격과 효과 검증, 개인정보 처리 방식이 구매 전환의 핵심 변수입니다.",
    "purchase_intent_changes": [
      {
        "persona_name": "김민수",
        "before_score": 4,
        "after_score": 6,
        "change_reason": "영어학원 대비 비용이 낮고 무료 체험이 있다면 부담이 줄어든다고 판단"
      }
    ]
  }
}
"""


def build_user_prompt(
    request: SimulationRequest,
    analysis: dict,
    debate_personas: list,
    summary_report: dict,
) -> str:
    return f"""
다음 제품에 대해 아래 대표 페르소나들이 서로의 의견을 듣고 토론하는 장면을 시뮬레이션하세요.

제품명: {request.product_name}
제품 설명: {request.product_description}
광고 카피: {request.ad_copy}

제품 분석 결과:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

모더레이터 요약 리포트 (전체 반응 참고용):
{json.dumps(summary_report, ensure_ascii=False, indent=2)}

토론에 참여하는 대표 페르소나와 각자의 기존 반응:
{json.dumps(debate_personas, ensure_ascii=False, indent=2)}

각 페르소나의 이름(name), 성향(reaction_type), 기존 반응(first_impression, positive_points, concerns,
purchase_intent_score)을 반드시 반영해서 발언을 작성하세요.

아래 JSON 구조에 맞춰 반환하세요.
{JSON_SCHEMA_HINT}
"""
