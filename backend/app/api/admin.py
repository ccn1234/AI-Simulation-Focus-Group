from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.simulation import AIUsageLog, Keyword, Simulation, SimulationKeyword, User
from app.security import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

class RoleUpdate(BaseModel):
    role: str

class KeywordRequest(BaseModel):
    value: str
    category: str = "general"
    synonyms: list[str] = []
    is_priority: bool = False
    is_excluded: bool = False

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    status_counts = dict(db.execute(select(Simulation.status, func.count(Simulation.id)).group_by(Simulation.status)).all())
    avg_score = db.scalar(select(func.avg(func.json_extract(Simulation.product_analysis, '$.overall_score'))))
    return {
        "users": db.scalar(select(func.count(User.id))) or 0,
        "simulations": db.scalar(select(func.count(Simulation.id))) or 0,
        "status_counts": status_counts,
        "average_score": float(avg_score) if avg_score is not None else None,
        "recent_simulations": _simulation_rows(db.scalars(select(Simulation).order_by(Simulation.created_at.desc()).limit(10)).all()),
        "ai_usage": {"tokens": db.scalar(select(func.sum(AIUsageLog.total_tokens))) or 0, "estimated_cost": db.scalar(select(func.sum(AIUsageLog.estimated_cost)))},
    }

def _simulation_rows(items):
    return [{"id": x.id, "user_id": x.user_id, "product_name": x.product_name, "status": x.status, "created_at": x.created_at, "completed_at": x.completed_at} for x in items]

@router.get("/users")
def users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return [{"id": x.id, "email": x.email, "role": x.role, "created_at": x.created_at, "simulation_count": len(x.simulations)} for x in db.scalars(select(User).order_by(User.created_at.desc())).all()]

@router.patch("/users/{user_id}/role")
def update_role(user_id: int, body: RoleUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if body.role not in {"USER", "ADMIN"}: raise HTTPException(400, "Role must be USER or ADMIN")
    if user_id == admin.id: raise HTTPException(400, "You cannot change your own role")
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "User not found")
    if user.role == "ADMIN" and body.role == "USER" and db.scalar(select(func.count(User.id)).where(User.role == "ADMIN")) <= 1: raise HTTPException(400, "At least one administrator is required")
    user.role = body.role; db.commit(); return {"id": user.id, "email": user.email, "role": user.role}

@router.get("/simulations")
def simulations(search: str | None = None, status: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    statement = select(Simulation).order_by(Simulation.created_at.desc())
    if search: statement = statement.where(or_(Simulation.product_name.ilike(f"%{search}%"), Simulation.product_description.ilike(f"%{search}%")))
    if status: statement = statement.where(Simulation.status == status)
    return _simulation_rows(db.scalars(statement).all())

@router.delete("/simulations/{simulation_id}", status_code=204)
def delete_simulation(simulation_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    item = db.get(Simulation, simulation_id)
    if not item: raise HTTPException(404, "Simulation not found")
    db.delete(item); db.commit()

@router.get("/ai-logs")
def ai_logs(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return [{"id": x.id, "simulation_id": x.simulation_id, "model_name": x.model_name, "total_tokens": x.total_tokens, "estimated_cost": x.estimated_cost, "created_at": x.created_at} for x in db.scalars(select(AIUsageLog).order_by(AIUsageLog.created_at.desc()).limit(limit)).all()]

@router.get("/keywords")
def keywords(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return [{"id": x.id, "value": x.value, "category": x.category, "synonyms": x.synonyms, "is_priority": x.is_priority, "is_excluded": x.is_excluded} for x in db.scalars(select(Keyword).order_by(Keyword.value)).all()]

@router.post("/keywords", status_code=201)
def create_keyword(body: KeywordRequest, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    value = body.value.strip()
    if not value: raise HTTPException(400, "Keyword cannot be empty")
    if db.scalar(select(Keyword).where(Keyword.value == value)): raise HTTPException(409, "Keyword already exists")
    item = Keyword(value=value, category=body.category, synonyms=body.synonyms, is_priority=body.is_priority, is_excluded=body.is_excluded); db.add(item); db.commit(); db.refresh(item); return {"id": item.id, "value": item.value, "category": item.category}

@router.patch("/keywords/{keyword_id}")
def update_keyword(keyword_id: int, body: KeywordRequest, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    item = db.get(Keyword, keyword_id)
    if not item: raise HTTPException(404, "Keyword not found")
    value = body.value.strip()
    if not value: raise HTTPException(400, "Keyword cannot be empty")
    item.value = value; item.category = body.category; item.synonyms = body.synonyms; item.is_priority = body.is_priority; item.is_excluded = body.is_excluded; db.commit(); return {"id": item.id, "value": item.value, "category": item.category}

@router.delete("/keywords/{keyword_id}", status_code=204)
def delete_keyword(keyword_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    item = db.get(Keyword, keyword_id)
    if not item: raise HTTPException(404, "Keyword not found")
    db.delete(item); db.commit()
