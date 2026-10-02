import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.data import DataStore
from app.main import create_app


REPO_ROOT = Path(__file__).resolve().parents[2]


def _client(narrative_writer=None) -> tuple[TestClient, DataStore]:
    store = DataStore(
        REPO_ROOT / "center_data",
        REPO_ROOT / "backend" / "test-var" / "api.duckdb",
    )
    store.connection.execute("DELETE FROM review_decisions")
    settings = Settings(
        data_dir=REPO_ROOT / "center_data",
        db_path=REPO_ROOT / "backend" / "test-var" / "api.duckdb",
        anthropic_api_key=None,
    )
    return TestClient(create_app(settings, store, narrative_writer=narrative_writer)), store


def test_investigate_demo_case_and_validation() -> None:
    client, store = _client()
    try:
        response = client.post("/investigate", json={"invoice_id": "INV0021439"})
        assert response.status_code == 200
        body = response.json()
        assert body["priority"]["value"] == "High"
        assert body["narrative"]["status"] == "unavailable"
        assert body["narrative"]["checklist"] == ""
        assert body["signals"]["duplicate"]["matches"][0]["invoice_id"] == "INV0046758"

        assert client.post("/investigate", json={"invoice_id": "UNKNOWN"}).status_code == 404
        assert client.post("/investigate", json={}).status_code == 422
    finally:
        store.close()


def test_decision_override_requires_reason_and_is_persisted() -> None:
    client, store = _client()
    try:
        missing_reason = client.post(
            "/investigations/INV0021439/decisions",
            json={
                "disposition": "escalate",
                "reviewer": "reviewer@example.com",
                "priority_override": "Medium",
            },
        )
        assert missing_reason.status_code == 422

        recorded = client.post(
            "/investigations/INV0021439/decisions",
            json={
                "disposition": "escalate",
                "note": "Compare the two records with procurement.",
                "reviewer": "reviewer@example.com",
                "priority_override": "Medium",
                "override_reason": "The duplicate is already paid and needs retrospective follow-up.",
            },
        )
        assert recorded.status_code == 200
        assert recorded.json()["priority"] == "Medium"
        history = client.get("/investigations/INV0021439/decisions")
        assert history.status_code == 200
        assert history.json()[0]["evidence_snapshot"]["invoice"]["invoice_id"] == "INV0021439"
    finally:
        store.close()


def test_saved_decision_keeps_the_narrative_that_was_shown() -> None:
    calls = {"n": 0}

    def writer(_payload: dict[str, object]) -> str:
        calls["n"] += 1
        if calls["n"] > 1:
            return json.dumps({"narrative": "This is fraud.", "checklist": "Verify IEX0004557."})
        return json.dumps(
            {
                "narrative": "INV0021439 has exception IEX0004557.",
                "checklist": "Verify IEX0004557.",
            }
        )

    client, store = _client(writer)
    try:
        investigated = client.post("/investigate", json={"invoice_id": "INV0021439"})
        assert investigated.status_code == 200
        shown = investigated.json()["narrative"]
        assert shown["status"] == "shown"
        assert calls["n"] == 1

        recorded = client.post(
            "/investigations/INV0021439/decisions",
            json={
                "disposition": "needs_more_info",
                "note": "Verify IEX0004557.",
                "reviewer": "reviewer@example.com",
                "narrative": shown,
            },
        )
        assert recorded.status_code == 200
        assert calls["n"] == 1
        assert recorded.json()["note"] == "Verify IEX0004557."
        snapshot = recorded.json()["evidence_snapshot"]["narrative"]
        assert snapshot["status"] == "shown"
        assert snapshot["text"] == "INV0021439 has exception IEX0004557."
        assert snapshot["checklist"] == ""
    finally:
        store.close()


def test_explain_is_unavailable_without_a_key() -> None:
    client, store = _client()
    try:
        response = client.post("/investigate/explain", json={"invoice_id": "INV0021439"})
        assert response.status_code == 503
        assert "ANTHROPIC_API_KEY" in response.json()["detail"]
    finally:
        store.close()
