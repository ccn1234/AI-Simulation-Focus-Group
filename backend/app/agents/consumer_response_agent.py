from app.agents.base import call_json_agent
from app.prompts.consumer_response_prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas.simulation import SimulationRequest


async def generate_responses(request: SimulationRequest, analysis: dict, personas: list) -> list:
    """각 페르소나 입장에서 제품/광고 카피에 대한 반응을 생성한다."""
    data = await call_json_agent(SYSTEM_PROMPT, build_user_prompt(request, analysis, personas), temperature=0.8, agent_name="consumer_response")
    return data["responses"]
