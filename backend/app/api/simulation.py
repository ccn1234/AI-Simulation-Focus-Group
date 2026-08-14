from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.repositories.simulation_repository import SimulationRepository
from app.services.simulation_persistence_service import create_persisted_simulation
from app.services.simulation_service import run_simulation
from app.models.simulation import User
from app.security import get_current_user
from app.services.keyword_insight_service import build_insights

router = APIRouter()


@router.post("/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest, user: User = Depends(get_current_user)):
    try:
        return await run_simulation(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulations", response_model=SimulationResponse)
async def create_simulation(request: SimulationRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        _, result = await create_persisted_simulation(db, request, user_id=user.id)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/simulations")
def list_simulations(
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
    search: str | None = None, status: str | None = None,
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    from app.models.simulation import Simulation
    statement = select(Simulation).order_by(Simulation.created_at.desc()).offset(offset).limit(limit)
    statement = statement.where(Simulation.user_id == user.id)
    if search:
        statement = statement.where(or_(Simulation.product_name.ilike(f"%{search}%"), Simulation.product_description.ilike(f"%{search}%")))
    if status:
        statement = statement.where(Simulation.status == status)
    simulations = list(db.scalars(statement))
    return [
        {
            "id": item.id,
            "product_name": item.product_name,
            "target_audience": item.target_audience,
            "status": item.status,
            "created_at": item.created_at,
            "completed_at": item.completed_at,
        }
        for item in simulations
    ]


@router.get("/simulations/compare")
def compare_simulations(ids: list[int] = Query(..., min_length=2, max_length=3), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=400, detail="Simulation IDs must be unique")
    simulations = [SimulationRepository(db).get(item_id) for item_id in ids]
    if any(item is None or item.user_id != user.id for item in simulations):
        raise HTTPException(status_code=404, detail="One or more simulations not found")
    return [
        {
            "id": item.id,
            "product_name": item.product_name,
            "status": item.status,
            "product_analysis": item.product_analysis,
            "summary_report": item.summary_report.data if item.summary_report else None,
            "discussion_result": item.discussion.data if item.discussion else None,
            "personas": [persona.profile for persona in item.personas],
            "responses": [persona.response.data for persona in item.personas if persona.response],
        }
        for item in simulations
    ]


@router.get("/simulations/{simulation_id}")
def get_simulation(simulation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    simulation = SimulationRepository(db).get(simulation_id)
    if not simulation or simulation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {
        "id": simulation.id,
        "product_name": simulation.product_name,
        "product_description": simulation.product_description,
        "target_audience": simulation.target_audience,
        "ad_copy": simulation.ad_copy,
        "status": simulation.status,
        "personas": [persona.profile for persona in simulation.personas],
        "responses": [persona.response.data for persona in simulation.personas if persona.response],
        "product_analysis": simulation.product_analysis,
        "summary_report": simulation.summary_report.data if simulation.summary_report else None,
        "discussion_result": simulation.discussion.data if simulation.discussion else None,
        "created_at": simulation.created_at,
        "completed_at": simulation.completed_at,
        "error_message": simulation.error_message,
    }


@router.get("/simulations/{simulation_id}/personas")
def get_personas(simulation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    simulation = SimulationRepository(db).get(simulation_id)
    if not simulation or simulation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return [{"persona": item.profile, "response": item.response.data if item.response else None} for item in simulation.personas]


@router.get("/simulations/{simulation_id}/report")
def get_report(simulation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    simulation = SimulationRepository(db).get(simulation_id)
    if not simulation or simulation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation.summary_report.data if simulation.summary_report else None


@router.get("/simulations/{simulation_id}/discussion")
def get_discussion(simulation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    simulation = SimulationRepository(db).get(simulation_id)
    if not simulation or simulation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation.discussion.data if simulation.discussion else None

@router.get("/simulations/{simulation_id}/insights")
def get_insights(simulation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    simulation = SimulationRepository(db).get(simulation_id)
    if not simulation or simulation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return build_insights(db, simulation)


@router.delete("/simulations/{simulation_id}", status_code=204)
def delete_simulation(simulation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    simulation = SimulationRepository(db).get(simulation_id)
    if not simulation or simulation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Simulation not found")
    db.delete(simulation)
    db.commit()

@router.post("/simulations/{simulation_id}/retry", response_model=SimulationResponse)
async def retry_simulation(simulation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    simulation = SimulationRepository(db).get(simulation_id)
    if not simulation or simulation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Simulation not found")
    if simulation.status != "failed":
        raise HTTPException(status_code=400, detail="Only failed simulations can be retried")
    request = SimulationRequest(product_name=simulation.product_name, product_description=simulation.product_description, target_audience=simulation.target_audience, ad_copy=simulation.ad_copy)
    _, result = await create_persisted_simulation(db, request, user_id=user.id)
    return result
