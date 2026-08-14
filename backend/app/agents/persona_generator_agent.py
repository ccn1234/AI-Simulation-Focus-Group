from app.agents.base import call_json_agent
from app.prompts.persona_generator_prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas.simulation import SimulationRequest

PERSONA_COUNT = 10

DEFAULT_PERSONA = {
    "name": "익명 소비자",
    "age": 30,
    "gender": "미상",
    "job": "직장인",
    "income_level": "중간",
    "personality": "보통",
    "pain_point": "",
    "purchase_barrier": "",
    "region": "수도권",
    "marital_status": "미상",
    "has_children": False,
    "lifestyle": "",
    "ai_familiarity": "중간",
    "brand_sensitivity": "중간",
    "price_sensitivity": "중간",
    "current_solutions": [],
    "decision_style": "실용형",
    "frequently_used_apps": [],
    "information_channels": [],
    "past_failure_experience": "",
    "reaction_type": "pragmatic",
}

_TRUE_TOKENS = {"true", "yes", "y", "예", "있음", "있다", "기혼"}
_FALSE_TOKENS = {"false", "no", "n", "아니오", "없음", "없다", "미혼"}


def _coerce_bool(value, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        token = value.strip().lower()
        if token in _TRUE_TOKENS:
            return True
        if token in _FALSE_TOKENS:
            return False
    if isinstance(value, list):
        return len(value) > 0
    return default


def _coerce_list(value) -> list:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _coerce_str(value, default: str) -> str:
    if isinstance(value, list):
        joined = ", ".join(str(item) for item in value if str(item).strip())
        return joined or default
    if value is None or value == "":
        return default
    return str(value)


def _normalize_persona(raw: dict, persona_id: int) -> dict:
    """OpenAI 응답에 필드가 빠지거나 타입이 어긋나도 항상 동일한 키 구조를 보장한다."""
    if not isinstance(raw, dict):
        raw = {}

    normalized: dict = {"id": persona_id}

    try:
        normalized["age"] = int(raw.get("age", DEFAULT_PERSONA["age"]))
    except (TypeError, ValueError):
        normalized["age"] = DEFAULT_PERSONA["age"]

    normalized["has_children"] = _coerce_bool(
        raw.get("has_children"), DEFAULT_PERSONA["has_children"]
    )

    for key, default in DEFAULT_PERSONA.items():
        if key in ("age", "has_children"):
            continue
        value = raw.get(key)
        if isinstance(default, list):
            normalized[key] = _coerce_list(value)
        else:
            normalized[key] = _coerce_str(value, default)

    return normalized


def _normalize_personas(raw_personas: list) -> list:
    if not isinstance(raw_personas, list):
        raw_personas = []

    personas = raw_personas[:PERSONA_COUNT]
    while len(personas) < PERSONA_COUNT:
        personas.append({})

    return [_normalize_persona(raw, index + 1) for index, raw in enumerate(personas)]


async def generate_personas(request: SimulationRequest, analysis: dict) -> list:
    """제품 분석 결과와 타겟 고객을 바탕으로 소비자 페르소나 10명을 생성한다."""
    try:
        data = await call_json_agent(SYSTEM_PROMPT, build_user_prompt(request, analysis), agent_name="persona_generator")
        raw_personas = data.get("personas", [])
    except ValueError:
        # OpenAI가 빈 응답을 주거나 JSON 파싱에 실패해도 기본값 페르소나로 시뮬레이션을 계속 진행한다.
        raw_personas = []

    return _normalize_personas(raw_personas)
