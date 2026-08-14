from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_description: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    ad_copy: Mapped[str] = mapped_column(Text, nullable=False)
    product_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    model_name: Mapped[str | None] = mapped_column(String(100))
    total_tokens: Mapped[int | None] = mapped_column(Integer)
    estimated_cost: Mapped[str | None] = mapped_column(String(40))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    personas: Mapped[list["Persona"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")
    summary_report: Mapped["SummaryReport | None"] = relationship(back_populates="simulation", uselist=False, cascade="all, delete-orphan")
    discussion: Mapped["Discussion | None"] = relationship(back_populates="simulation", uselist=False, cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="USER")
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    auth_provider: Mapped[str] = mapped_column(String(20), nullable=False, default="password")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    simulations: Mapped[list[Simulation]] = relationship(backref="user", cascade="all, delete-orphan")


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    persona_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    profile: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    simulation: Mapped[Simulation] = relationship(back_populates="personas")
    response: Mapped["PersonaResponse | None"] = relationship(back_populates="persona", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("simulation_id", "persona_number", name="uq_persona_simulation_number"),)


class PersonaResponse(Base):
    __tablename__ = "persona_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    persona: Mapped[Persona] = relationship(back_populates="response")


class SummaryReport(Base):
    __tablename__ = "summary_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, unique=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    simulation: Mapped[Simulation] = relationship(back_populates="summary_report")


class Discussion(Base):
    __tablename__ = "discussions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, unique=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    simulation: Mapped[Simulation] = relationship(back_populates="discussion")


class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="general")
    synonyms: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_priority: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_excluded: Mapped[bool] = mapped_column(default=False, nullable=False)


class SimulationKeyword(Base):
    __tablename__ = "simulation_keywords"
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id", ondelete="CASCADE"), primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id", ondelete="CASCADE"), index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, default="unknown")
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    total_tokens: Mapped[int | None] = mapped_column(Integer)
    estimated_cost: Mapped[str | None] = mapped_column(String(40))
    elapsed_ms: Mapped[int | None] = mapped_column(Integer)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="succeeded")
    error_type: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
