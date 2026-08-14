from app.agents.product_analyzer_agent import analyze_product
from app.agents.persona_generator_agent import generate_personas
from app.agents.consumer_response_agent import generate_responses
from app.agents.moderator_agent import summarize
from app.agents.discussion_agent import run_discussion
from app.schemas.simulation import SimulationRequest, SimulationResponse


async def run_simulation(request: SimulationRequest) -> SimulationResponse:
    """5단계 에이전트 파이프라인을 순서대로 실행해 시뮬레이션 결과를 생성한다.

    ProductAnalyzer -> PersonaGenerator -> ConsumerResponse -> Moderator -> Discussion
    각 단계는 이전 단계의 결과물을 입력으로 받는다.
    """
    analysis = await analyze_product(request)
    personas = await generate_personas(request, analysis)
    responses = await generate_responses(request, analysis, personas)
    summary = await summarize(personas, responses)
    discussion = await run_discussion(request, analysis, personas, responses, summary)

    return SimulationResponse.model_validate({
        "product_analysis": analysis,
        "personas": personas,
        "responses": responses,
        "summary_report": summary,
        "discussion_result": discussion,
    })
