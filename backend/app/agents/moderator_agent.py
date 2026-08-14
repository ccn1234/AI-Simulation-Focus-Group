from app.agents.base import call_json_agent
from app.prompts.moderator_prompts import SYSTEM_PROMPT, build_user_prompt


async def summarize(personas: list, responses: list) -> dict:
    """전체 페르소나 반응을 종합해 모더레이터 요약 리포트를 생성한다."""
    return await call_json_agent(SYSTEM_PROMPT, build_user_prompt(personas, responses), agent_name="moderator")
