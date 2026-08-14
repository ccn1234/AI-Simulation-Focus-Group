from typing import List
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    product_name: str = Field(..., min_length=1)
    product_description: str = Field(..., min_length=1)
    target_audience: str = Field(..., min_length=1)
    ad_copy: str = Field(..., min_length=1)


class ProductAnalysis(BaseModel):
    core_value_proposition: str
    expected_purchase_motivations: List[str]
    expected_resistance_factors: List[str]
    main_competitors_or_alternatives: List[str]
    copy_strengths: List[str]
    copy_weaknesses: List[str]
    target_fit_summary: str


class Persona(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    job: str
    income_level: str
    personality: str
    pain_point: str
    purchase_barrier: str
    region: str
    marital_status: str
    has_children: bool
    lifestyle: str
    ai_familiarity: str
    brand_sensitivity: str
    price_sensitivity: str
    current_solutions: List[str]
    decision_style: str
    frequently_used_apps: List[str]
    information_channels: List[str]
    past_failure_experience: str
    reaction_type: str


class PersonaResponse(BaseModel):
    persona_id: int
    first_impression: str
    positive_points: List[str]
    concerns: List[str]
    purchase_intent_score: int = Field(..., ge=1, le=10)
    memorable_quote: str
    suggested_improvement: str


class SummaryReport(BaseModel):
    overall_score: int = Field(..., ge=1, le=10)
    key_insights: List[str]
    key_positive_reactions: List[str]
    key_negative_reactions: List[str]
    strongest_target_segment: str
    weakest_point: str
    improvement_priorities: List[str]
    recommended_next_actions: List[str]


class DiscussionMessage(BaseModel):
    speaker_name: str
    speaker_role: str
    message: str
    stance: str
    related_issue: str


class PurchaseIntentChange(BaseModel):
    persona_name: str
    before_score: int
    after_score: int
    change_reason: str


class DiscussionSummary(BaseModel):
    main_conflicts: List[str]
    agreements: List[str]
    changed_opinions: List[str]
    final_group_consensus: str
    purchase_intent_changes: List[PurchaseIntentChange]


class DiscussionResult(BaseModel):
    discussion_messages: List[DiscussionMessage]
    discussion_summary: DiscussionSummary


class SimulationResponse(BaseModel):
    product_analysis: ProductAnalysis
    personas: List[Persona]
    responses: List[PersonaResponse]
    summary_report: SummaryReport
    discussion_result: DiscussionResult
