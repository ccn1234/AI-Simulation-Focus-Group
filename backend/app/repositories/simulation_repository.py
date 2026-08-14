from datetime import datetime

from sqlalchemy import select
import json
import re
from sqlalchemy.orm import Session

from app.models.simulation import Simulation
from app.models.simulation import Discussion, Keyword, Persona, PersonaResponse, SimulationKeyword, SummaryReport

STOPWORDS = {"그리고", "하지만", "대한", "있는", "있다", "하는", "하면", "정말", "매우", "입니다", "합니다", "으로", "에서", "the", "and", "with", "for", "this", "that"}
KOREAN_SUFFIXES = ("으로", "에서", "에게", "까지", "부터", "처럼", "보다", "하고", "하며", "하면", "하는", "한", "은", "는", "이", "가", "을", "를", "에", "도", "만")

def extract_keywords(*texts: str) -> list[str]:
    tokens: set[str] = set()
    for text in texts:
        for token in re.findall(r"[가-힣]{2,}|[A-Za-z][A-Za-z0-9-]{2,}", text or ""):
            normalized = token.lower().strip("-_")
            if normalized.endswith(KOREAN_SUFFIXES):
                for suffix in KOREAN_SUFFIXES:
                    if normalized.endswith(suffix) and len(normalized) - len(suffix) >= 2:
                        normalized = normalized[:-len(suffix)]
                        break
            if normalized not in STOPWORDS:
                tokens.add(normalized)
    return sorted(tokens)[:30]


class SimulationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **data) -> Simulation:
        simulation = Simulation(**data)
        self.db.add(simulation)
        self.db.flush()
        return simulation

    def get(self, simulation_id: int) -> Simulation | None:
        return self.db.scalar(select(Simulation).where(Simulation.id == simulation_id))

    def list(self, limit: int = 20, offset: int = 0) -> list[Simulation]:
        statement = select(Simulation).order_by(Simulation.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(statement))

    def update_status(self, simulation: Simulation, status: str, error_message: str | None = None) -> Simulation:
        simulation.status = status
        simulation.error_message = error_message
        if status == "running":
            simulation.started_at = datetime.utcnow()
        if status in {"succeeded", "failed"}:
            simulation.completed_at = datetime.utcnow()
        self.db.flush()
        return simulation

    def save_result(self, simulation: Simulation, result: dict) -> Simulation:
        analysis = result.get("product_analysis", {})
        personas = result.get("personas", [])
        responses = result.get("responses", [])

        response_by_persona = {item.get("persona_id"): item for item in responses if isinstance(item, dict)}
        for persona_data in personas:
            if not isinstance(persona_data, dict):
                continue
            persona = Persona(
                simulation_id=simulation.id,
                persona_number=int(persona_data.get("id", len(simulation.personas) + 1)),
                name=str(persona_data.get("name", "Unknown Persona")),
                age=int(persona_data.get("age", 0)),
                profile=persona_data,
            )
            response_data = response_by_persona.get(persona_data.get("id"))
            if response_data:
                persona.response = PersonaResponse(data=response_data)
            simulation.personas.append(persona)

        simulation.summary_report = SummaryReport(data=result.get("summary_report", {}))
        simulation.discussion = Discussion(data=result.get("discussion_result", {}))
        simulation.product_analysis = analysis
        keyword_values = extract_keywords(simulation.product_name, simulation.product_description, simulation.target_audience, simulation.ad_copy)
        for value in keyword_values:
            keyword = self.db.scalar(select(Keyword).where(Keyword.value == value))
            if not keyword:
                keyword = Keyword(value=value)
                self.db.add(keyword)
                self.db.flush()
            self.db.add(SimulationKeyword(simulation_id=simulation.id, keyword_id=keyword.id))
        simulation.status = "succeeded"
        simulation.completed_at = datetime.utcnow()
        self.db.flush()
        return simulation
