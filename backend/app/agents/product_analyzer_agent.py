from app.agents.base import call_json_agent
from app.prompts.product_analyzer_prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas.simulation import SimulationRequest

DEFAULT_ANALYSIS = {
    "core_value_proposition": "",
    "expected_purchase_motivations": [],
    "expected_resistance_factors": [],
    "main_competitors_or_alternatives": [],
    "copy_strengths": [],
    "copy_weaknesses": [],
    "target_fit_summary": "",
}


def _normalize_analysis(raw: dict) -> dict:
    """OpenAI 응답에 키가 빠지거나 타입이 어긋나도 항상 동일한 키 구조를 보장한다."""
    normalized = {}
    for key, default in DEFAULT_ANALYSIS.items():
        value = raw.get(key, default)
        if isinstance(default, list):
            if isinstance(value, list):
                normalized[key] = [str(item) for item in value]
            elif value:
                normalized[key] = [str(value)]
            else:
                normalized[key] = []
        else:
            normalized[key] = str(value) if value else default
    return normalized


async def analyze_product(request: SimulationRequest) -> dict:
    """제품/광고 카피를 분석해 가치제안, 구매동기, 저항요소, 비교대상을 도출한다."""
    try:
        raw = await call_json_agent(SYSTEM_PROMPT, build_user_prompt(request), agent_name="product_analyzer")
    except ValueError:
        # OpenAI가 빈 응답을 주거나 JSON 파싱에 실패해도 기본값으로 시뮬레이션을 계속 진행한다.
        raw = {}
    return _normalize_analysis(raw)
