import asyncio

import pytest
from sqlalchemy import select

from app.models.simulation import Simulation
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.services.simulation_persistence_service import (
    create_simulation_job,
    process_simulation_job,
)


SIMULATION_PAYLOAD = {
    "product_name": "Test product",
    "product_description": "A product used to test the simulation API.",
    "target_audience": "Office workers in their twenties",
    "ad_copy": "Save time with this simple product.",
}


def _login(client, email):
    client.post(
        "/auth/signup",
        json={"email": email, "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "password123"},
    )
    return response.json()["access_token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def _fake_result():
    return {
        "product_analysis": {
            "core_value_proposition": "Saves time for busy users.",
            "expected_purchase_motivations": ["Time savings"],
            "expected_resistance_factors": ["Price"],
            "main_competitors_or_alternatives": ["Manual work"],
            "copy_strengths": ["Clear message"],
            "copy_weaknesses": ["Needs more detail"],
            "target_fit_summary": "Suitable for office workers.",
        },
        "personas": [],
        "responses": [],
        "summary_report": {
            "overall_score": 7,
            "key_insights": ["Time savings are the main benefit."],
            "key_positive_reactions": ["It looks easy to use."],
            "key_negative_reactions": ["The price may be a concern."],
            "strongest_target_segment": "Office workers in their twenties",
            "weakest_point": "Price explanation",
            "improvement_priorities": ["Clarify the pricing policy"],
            "recommended_next_actions": ["Offer a free trial"],
        },
        "discussion_result": {
            "discussion_messages": [],
            "discussion_summary": {
                "main_conflicts": [],
                "agreements": [],
                "changed_opinions": [],
                "final_group_consensus": "Conditionally positive",
                "purchase_intent_changes": [],
            },
        },
    }


def _configure_successful_worker(monkeypatch, db_session_factory, observed_statuses=None):
    import app.services.simulation_persistence_service as persistence_service

    monkeypatch.setattr(persistence_service, "SessionLocal", db_session_factory)

    async def fake_run_simulation(_request):
        if observed_statuses is not None:
            with db_session_factory() as db:
                observed_statuses.append(
                    db.scalar(select(Simulation.status).order_by(Simulation.id.desc()))
                )
        return SimulationResponse.model_validate(_fake_result())

    monkeypatch.setattr(persistence_service, "run_simulation", fake_run_simulation)


def test_create_returns_job_and_background_worker_saves_result(
    client,
    db_session_factory,
    monkeypatch,
):
    observed_statuses = []
    _configure_successful_worker(monkeypatch, db_session_factory, observed_statuses)
    token = _login(client, "simulation@example.com")

    created = client.post(
        "/simulations",
        json=SIMULATION_PAYLOAD,
        headers=_headers(token),
    )

    assert created.status_code == 202
    assert created.json()["status"] == "pending"
    simulation_id = created.json()["id"]
    assert observed_statuses == ["running"]

    detail = client.get(f"/simulations/{simulation_id}", headers=_headers(token))
    assert detail.status_code == 200
    assert detail.json()["status"] == "succeeded"
    assert detail.json()["summary_report"]["overall_score"] == 7
    assert detail.json()["started_at"] is not None
    assert detail.json()["completed_at"] is not None


def test_background_worker_marks_failed_job(db_session_factory, monkeypatch):
    import app.services.simulation_persistence_service as persistence_service

    request = SimulationRequest.model_validate(SIMULATION_PAYLOAD)
    with db_session_factory() as db:
        simulation = create_simulation_job(db, request)
        simulation_id = simulation.id

    monkeypatch.setattr(persistence_service, "SessionLocal", db_session_factory)

    async def failing_run_simulation(_request):
        raise RuntimeError("Fake AI failure")

    monkeypatch.setattr(persistence_service, "run_simulation", failing_run_simulation)

    with pytest.raises(RuntimeError, match="Fake AI failure"):
        asyncio.run(process_simulation_job(simulation_id))

    with db_session_factory() as db:
        failed = db.get(Simulation, simulation_id)
        assert failed.status == "failed"
        assert failed.error_message == "Fake AI failure"
        assert failed.started_at is not None
        assert failed.completed_at is not None


def test_simulation_detail_and_delete(client, db_session_factory, monkeypatch):
    _configure_successful_worker(monkeypatch, db_session_factory)
    token = _login(client, "detail@example.com")
    created = client.post(
        "/simulations",
        json=SIMULATION_PAYLOAD,
        headers=_headers(token),
    )
    simulation_id = created.json()["id"]

    detail = client.get(f"/simulations/{simulation_id}", headers=_headers(token))
    assert detail.status_code == 200
    assert detail.json()["product_name"] == "Test product"

    deleted = client.delete(f"/simulations/{simulation_id}", headers=_headers(token))
    assert deleted.status_code == 204
    assert client.get(f"/simulations/{simulation_id}", headers=_headers(token)).status_code == 404


def test_retry_returns_new_job_id(client, db_session_factory, monkeypatch):
    _configure_successful_worker(monkeypatch, db_session_factory)
    token = _login(client, "retry@example.com")
    created = client.post(
        "/simulations",
        json=SIMULATION_PAYLOAD,
        headers=_headers(token),
    )
    original_id = created.json()["id"]

    with db_session_factory() as db:
        original = db.get(Simulation, original_id)
        original.status = "failed"
        original.error_message = "Previous failure"
        db.commit()

    retried = client.post(
        f"/simulations/{original_id}/retry",
        headers=_headers(token),
    )

    assert retried.status_code == 202
    assert retried.json()["status"] == "pending"
    assert retried.json()["id"] != original_id


def test_user_cannot_read_another_users_simulation(
    client,
    db_session_factory,
    monkeypatch,
):
    _configure_successful_worker(monkeypatch, db_session_factory)
    first_token = _login(client, "owner@example.com")
    second_token = _login(client, "other@example.com")
    created = client.post(
        "/simulations",
        json=SIMULATION_PAYLOAD,
        headers=_headers(first_token),
    )

    response = client.get(
        f"/simulations/{created.json()['id']}",
        headers=_headers(second_token),
    )

    assert response.status_code == 404
