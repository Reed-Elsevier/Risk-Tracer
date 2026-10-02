from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.data import DataStore
from app.main import create_app


REPO_ROOT = Path(__file__).resolve().parents[2]


def _client() -> tuple[TestClient, DataStore]:
    store = DataStore(
        REPO_ROOT / "center_data",
        REPO_ROOT / "backend" / "test-var" / "api.duckdb",
    )
    store.connection.execute("DELETE FROM review_decisions")
    settings = Settings(
        data_dir=REPO_ROOT / "center_data",
        db_path=REPO_ROOT / "backend" / "test-var" / "api.duckdb",
        openai_api_key=None,
    )
    return TestClient(create_app(settings, store)), store


def test_investigate_demo_case_and_validation() -> None:
    client, store = _client()
    try:
        response = client.post("/investigate", json={"invoice_id": "INV0021439"})
        assert response.status_code == 200
        body = response.json()
        assert body["priority"]["value"] == "High"
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


def test_explain_is_unavailable_without_a_key() -> None:
    client, store = _client()
    try:
        response = client.post("/investigate/explain", json={"invoice_id": "INV0021439"})
        assert response.status_code == 503
        assert "OPENAI_API_KEY" in response.json()["detail"]
    finally:
        store.close()
