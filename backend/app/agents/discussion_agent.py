from app.agents.base import call_json_agent
from app.prompts.discussion_prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas.simulation import SimulationRequest

MAX_DEBATE_PERSONAS = 6
MIN_DEBATE_PERSONAS = 5

ALLOWED_STANCES = {"agree", "disagree", "neutral", "changed_mind", "challenge", "support"}
ALLOWED_ISSUES = {"price", "trust", "privacy", "convenience", "effectiveness", "habit", "brand"}

DEFAULT_SUMMARY = {
    "main_conflicts": [],
    "agreements": [],
    "changed_opinions": [],
    "final_group_consensus": "",
    "purchase_intent_changes": [],
}


def _select_debate_personas(personas: list, responses: list) -> list:
    """구매의향 상/중/하와 reaction_type 다양성을 기준으로 토론 대표 페르소나 5~6명을 선별한다."""
    if not isinstance(personas, list) or not isinstance(responses, list):
        return []

    persona_map = {p.get("id"): p for p in personas if isinstance(p, dict)}

    scored = []
    for response in responses:
        if not isinstance(response, dict):
            continue
        persona = persona_map.get(response.get("persona_id"))
        if not persona:
            continue
        try:
            score = int(response.get("purchase_intent_score", 0))
        except (TypeError, ValueError):
            score = 0
        scored.append({"persona": persona, "response": response, "score": score})

    if not scored:
        return []

    scored.sort(key=lambda item: item["score"], reverse=True)

    selected: dict = {}

    def add(item):
        persona_id = item["persona"].get("id")
        if persona_id is not None and persona_id not in selected:
            selected[persona_id] = item

    for item in scored[:2]:
        add(item)
    for item in scored[-2:]:
        add(item)

    mid_start = max(0, len(scored) // 2 - 1)
    for item in scored[mid_start:mid_start + 2]:
        add(item)

    used_types = {item["persona"].get("reaction_type") for item in selected.values()}
    for item in scored:
        if len(selected) >= MAX_DEBATE_PERSONAS:
            break
        persona_id = item["persona"].get("id")
        if persona_id in selected:
            continue
        if item["persona"].get("reaction_type") not in used_types:
            add(item)
            used_types.add(item["persona"].get("reaction_type"))

    for item in scored:
        if len(selected) >= MIN_DEBATE_PERSONAS:
            break
        add(item)

    ordered = sorted(selected.values(), key=lambda item: item["score"], reverse=True)
    return ordered[:MAX_DEBATE_PERSONAS]


def _build_debate_input(debate_personas: list) -> list:
    debate_input = []
    for item in debate_personas:
        persona = item["persona"]
        response = item["response"]
        debate_input.append({
            "name": persona.get("name"),
            "age": persona.get("age"),
            "job": persona.get("job"),
            "reaction_type": persona.get("reaction_type"),
            "price_sensitivity": persona.get("price_sensitivity"),
            "ai_familiarity": persona.get("ai_familiarity"),
            "brand_sensitivity": persona.get("brand_sensitivity"),
            "decision_style": persona.get("decision_style"),
            "current_solutions": persona.get("current_solutions"),
            "past_failure_experience": persona.get("past_failure_experience"),
            "first_impression": response.get("first_impression"),
            "positive_points": response.get("positive_points"),
            "concerns": response.get("concerns"),
            "purchase_intent_score": response.get("purchase_intent_score"),
            "memorable_quote": response.get("memorable_quote"),
        })
    return debate_input


def _coerce_list_of_str(value) -> list:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def _normalize_message(raw: dict) -> dict:
    if not isinstance(raw, dict):
        return {}

    message = str(raw.get("message") or "").strip()
    if not message:
        return {}

    stance = str(raw.get("stance") or "").strip().lower()
    if stance not in ALLOWED_STANCES:
        stance = "neutral"

    related_issue = str(raw.get("related_issue") or "").strip().lower()
    if related_issue not in ALLOWED_ISSUES:
        related_issue = "effectiveness"

    return {
        "speaker_name": str(raw.get("speaker_name") or "익명 참가자"),
        "speaker_role": str(raw.get("speaker_role") or ""),
        "message": message,
        "stance": stance,
        "related_issue": related_issue,
    }


def _normalize_messages(raw_messages) -> list:
    if not isinstance(raw_messages, list):
        return []

    normalized = []
    for raw in raw_messages:
        message = _normalize_message(raw)
        if message:
            normalized.append(message)
    return normalized[:12]


def _clamp_score(value) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 5
    return max(1, min(10, score))


def _normalize_intent_change(raw: dict) -> dict:
    if not isinstance(raw, dict):
        return {}

    persona_name = str(raw.get("persona_name") or "").strip()
    if not persona_name:
        return {}

    return {
        "persona_name": persona_name,
        "before_score": _clamp_score(raw.get("before_score")),
        "after_score": _clamp_score(raw.get("after_score")),
        "change_reason": str(raw.get("change_reason") or ""),
    }


def _normalize_summary(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raw = {}

    raw_changes = raw.get("purchase_intent_changes")
    changes = []
    if isinstance(raw_changes, list):
        for item in raw_changes:
            normalized = _normalize_intent_change(item)
            if normalized:
                changes.append(normalized)

    return {
        "main_conflicts": _coerce_list_of_str(raw.get("main_conflicts")),
        "agreements": _coerce_list_of_str(raw.get("agreements")),
        "changed_opinions": _coerce_list_of_str(raw.get("changed_opinions")),
        "final_group_consensus": str(raw.get("final_group_consensus") or ""),
        "purchase_intent_changes": changes,
    }


async def run_discussion(
    request: SimulationRequest,
    analysis: dict,
    personas: list,
    responses: list,
    summary_report: dict,
) -> dict:
    """대표 페르소나를 선별해 소비자 간 토론을 생성하고 결과를 정규화한다."""
    debate_personas = _select_debate_personas(personas, responses)
    if not debate_personas:
        return {"discussion_messages": [], "discussion_summary": dict(DEFAULT_SUMMARY)}

    debate_input = _build_debate_input(debate_personas)

    try:
        data = await call_json_agent(
            SYSTEM_PROMPT,
            build_user_prompt(request, analysis, debate_input, summary_report),
            temperature=0.8, agent_name="discussion",
        )
    except ValueError:
        # OpenAI가 빈 응답을 주거나 JSON 파싱에 실패해도 기본값으로 시뮬레이션을 계속 진행한다.
        data = {}

    return {
        "discussion_messages": _normalize_messages(data.get("discussion_messages")),
        "discussion_summary": _normalize_summary(data.get("discussion_summary")),
    }
