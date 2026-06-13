"""HTTP API and static serving."""

from __future__ import annotations

import pytest

from web.app import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"
    assert body["roles"] == 8
    assert body["model_configured"] is False  # scrubbed by conftest


def test_roles_listing(client):
    body = client.get("/api/roles").get_json()
    assert len(body["roles"]) == 8


def test_assessment_requires_known_role(client):
    res = client.post("/api/assessment", json={"role_id": "ceo"})
    assert res.status_code == 400


def test_assessment_and_result_flow(client):
    start = client.post("/api/assessment", json={"role_id": "wireless_network_engineer"}).get_json()
    assert start["questions"]
    answers = [
        {"competency_id": q["competency_id"], "question": q["question"], "answer": "WPA3 with 802.1X and a RADIUS server, separate guest SSID and VLAN."}
        for q in start["questions"]
    ]
    result = client.post(
        "/api/result", json={"role_id": "wireless_network_engineer", "answers": answers}
    ).get_json()
    assert 0 <= result["readiness_percent"] <= 100
    assert result["learning_plans"]


def test_result_rejects_empty_answers(client):
    res = client.post("/api/result", json={"role_id": "network_engineer", "answers": []})
    assert res.status_code == 400


def test_result_caps_answer_count(client):
    answers = [{"competency_id": "routing", "question": "q", "answer": "a"} for _ in range(50)]
    res = client.post("/api/result", json={"role_id": "network_engineer", "answers": answers})
    assert res.status_code == 400


def test_static_route_does_not_leak_source(client):
    # An encoded traversal must not return Python source.
    res = client.get("/assets/..%2f..%2fapp.py")
    assert res.status_code == 404
    assert b"create_app" not in res.data
