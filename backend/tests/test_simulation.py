from app.models.simulation import Simulation


SIMULATION_PAYLOAD = {
    "product_name": "테스트 앱",
    "product_description": "테스트용 상품 설명입니다.",
    "target_audience": "20대 직장인",
    "ad_copy": "더 빠르고 편하게 사용하세요.",
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
            "core_value_proposition": "업무 시간을 줄여주는 앱",
            "expected_purchase_motivations": ["시간 절약"],
            "expected_resistance_factors": ["가격"],
            "main_competitors_or_alternatives": ["수작업"],
            "copy_strengths": ["명확한 메시지"],
            "copy_weaknesses": ["구체적 사례 부족"],
            "target_fit_summary": "직장인에게 적합합니다.",
        },
        "personas": [],
        "responses": [],
        "summary_report": {
            "overall_score": 7,
            "key_insights": ["시간 절약이 핵심입니다."],
            "key_positive_reactions": ["사용이 쉬워 보입니다."],
            "key_negative_reactions": ["가격이 걱정됩니다."],
            "strongest_target_segment": "20대 직장인",
            "weakest_point": "가격 설명",
            "improvement_priorities": ["가격 정책 보완"],
            "recommended_next_actions": ["무료 체험 제공"],
        },
        "discussion_result": {
            "discussion_messages": [],
            "discussion_summary": {
                "main_conflicts": [],
                "agreements": [],
                "changed_opinions": [],
                "final_group_consensus": "조건부 긍정",
                "purchase_intent_changes": [],
            },
        },
    }


async def _fake_create_persisted_simulation(db, request, user_id):
    item = Simulation(
        user_id=user_id,
        product_name=request.product_name,
        product_description=request.product_description,
        target_audience=request.target_audience,
        ad_copy=request.ad_copy,
        product_analysis=_fake_result()["product_analysis"],
        status="succeeded",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item, _fake_result()


def test_create_and_list_simulation_without_calling_openai(client, monkeypatch):
    import app.api.simulation as simulation_api

    monkeypatch.setattr(
        simulation_api,
        "create_persisted_simulation",
        _fake_create_persisted_simulation,
    )
    token = _login(client, "simulation@example.com")

    created = client.post(
        "/simulations",
        json=SIMULATION_PAYLOAD,
        headers=_headers(token),
    )

    assert created.status_code == 200
    assert created.json()["summary_report"]["overall_score"] == 7

    listed = client.get("/simulations", headers=_headers(token))
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["product_name"] == "테스트 앱"


def test_simulation_detail_and_delete(client, monkeypatch):
    import app.api.simulation as simulation_api

    monkeypatch.setattr(
        simulation_api,
        "create_persisted_simulation",
        _fake_create_persisted_simulation,
    )
    token = _login(client, "detail@example.com")
    created = client.post(
        "/simulations",
        json=SIMULATION_PAYLOAD,
        headers=_headers(token),
    )
    simulation_id = created.json().get("id")

    # The endpoint response is intentionally checked by fetching the list,
    # because the service response schema does not expose the persistence ID.
    simulation_id = client.get("/simulations", headers=_headers(token)).json()[0]["id"]
    detail = client.get(f"/simulations/{simulation_id}", headers=_headers(token))
    assert detail.status_code == 200
    assert detail.json()["product_name"] == "테스트 앱"

    deleted = client.delete(f"/simulations/{simulation_id}", headers=_headers(token))
    assert deleted.status_code == 204
    assert client.get(f"/simulations/{simulation_id}", headers=_headers(token)).status_code == 404


def test_user_cannot_read_another_users_simulation(client, monkeypatch):
    import app.api.simulation as simulation_api

    monkeypatch.setattr(
        simulation_api,
        "create_persisted_simulation",
        _fake_create_persisted_simulation,
    )
    first_token = _login(client, "owner@example.com")
    second_token = _login(client, "other@example.com")
    client.post("/simulations", json=SIMULATION_PAYLOAD, headers=_headers(first_token))
    simulation_id = client.get("/simulations", headers=_headers(first_token)).json()[0]["id"]

    response = client.get(f"/simulations/{simulation_id}", headers=_headers(second_token))

    assert response.status_code == 404
