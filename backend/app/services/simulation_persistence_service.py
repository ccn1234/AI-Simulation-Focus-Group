from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.repositories.simulation_repository import SimulationRepository
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.services.simulation_service import run_simulation
from app.agents.base import end_usage_context, start_usage_context
from app.config import AI_INPUT_COST_PER_1K, AI_OUTPUT_COST_PER_1K
from app.models.simulation import AIUsageLog, Simulation


def create_simulation_job(
    db: Session,
    request: SimulationRequest,
    user_id: int | None = None,
) -> Simulation:
    repository = SimulationRepository(db)
    simulation = repository.create(
        product_name=request.product_name,
        product_description=request.product_description,
        target_audience=request.target_audience,
        ad_copy=request.ad_copy,
        user_id=user_id,
        status="pending",
    )
    db.commit()
    db.refresh(simulation)
    return simulation


async def process_simulation_job(simulation_id: int) -> SimulationResponse:
    db = SessionLocal()
    repository = SimulationRepository(db)
    simulation = repository.get(simulation_id)
    if simulation is None:
        db.close()
        raise ValueError(f"Simulation {simulation_id} not found")

    request = SimulationRequest(
        product_name=simulation.product_name,
        product_description=simulation.product_description,
        target_audience=simulation.target_audience,
        ad_copy=simulation.ad_copy,
    )

    try:
        repository.update_status(simulation, "running")
        db.commit()
        usage_token = start_usage_context()
        try:
            result = await run_simulation(request)
        finally:
            usage_records = end_usage_context(usage_token)
            for record in usage_records:
                prompt = record.get("prompt_tokens") or 0; completion = record.get("completion_tokens") or 0
                cost = (prompt / 1000 * AI_INPUT_COST_PER_1K) + (completion / 1000 * AI_OUTPUT_COST_PER_1K)
                db.add(AIUsageLog(simulation_id=simulation.id, estimated_cost=f"{cost:.8f}", **record))
        repository.save_result(simulation, result.model_dump())
        db.commit()
        return result
    except Exception as exc:
        db.rollback()
        simulation = repository.get(simulation.id)
        if simulation:
            repository.update_status(simulation, "failed", str(exc))
            db.commit()
        raise
    finally:
        db.close()


async def create_persisted_simulation(
    db: Session,
    request: SimulationRequest,
    user_id: int | None = None,
):
    """Temporary compatibility wrapper for synchronous API callers."""
    simulation = create_simulation_job(db, request, user_id=user_id)
    result = await process_simulation_job(simulation.id)
    db.refresh(simulation)
    return simulation, result
