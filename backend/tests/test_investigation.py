import json
from pathlib import Path

from app.data import DataStore
from app.investigation import build_investigation


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_demo_invoice_assembles_high_priority_investigation() -> None:
    store = DataStore(
        REPO_ROOT / "center_data",
        REPO_ROOT / "backend" / "test-var" / "risktracer.duckdb",
    )
    try:
        investigation = build_investigation("INV0021439", store)
    finally:
        store.close()

    assert investigation.invoice.invoice_id == "INV0021439"
    assert investigation.supplier.supplier_name == "Torvale Technologies B.V."
    assert investigation.priority.value == "High"
    assert investigation.signals.duplicate.matches[0].invoice_id == "INV0046758"
    assert investigation.signals.duplicate.matches[0].payment.payment_id == "PAY0041819"
    exposure = investigation.signals.watchlist.exposures[0]
    assert [link.ownership_link_id for link in exposure.links] == [
        "OWN0009353",
        "OWN0003041",
    ]
    assert exposure.watchlist.watchlist_entry_id == "WL003070"
    assert not investigation.signals.po_integrity.reasons
    assert investigation.signals.exceptions[0].exception_id == "IEX0004557"
    assert investigation.narrative.status == "unavailable"
    assert investigation.narrative.text == ""
    assert investigation.narrative.checklist == ""


def test_narrative_uses_supplier_history_counts_and_leaves_priority_unchanged() -> None:
    seen: dict[str, object] = {}

    def writer(payload: dict[str, object]) -> str:
        seen["payload"] = payload
        return json.dumps(
            {
                "narrative": "INV0021439 has exception IEX0004557.",
                "checklist": "Verify IEX0004557.",
            }
        )

    store = DataStore(
        REPO_ROOT / "center_data",
        REPO_ROOT / "backend" / "test-var" / "risktracer.duckdb",
    )
    try:
        investigation = build_investigation("INV0021439", store, narrative_writer=writer)
    finally:
        store.close()

    payload = seen["payload"]
    assert isinstance(payload, dict)
    assert "priority" not in payload
    assert payload["supplier_history"]["other_invoice_count"] == 9707
    assert "ENT007185" in payload["allowed_source_ids"]
    assert "EMP002195" not in payload["allowed_source_ids"]
    assert investigation.priority.value == "High"
    assert investigation.narrative.status == "shown"
    assert investigation.narrative.text == "INV0021439 has exception IEX0004557."
    assert investigation.narrative.checklist == "Verify IEX0004557."
    assert investigation.narrative.source_ids == ["INV0021439", "IEX0004557"]


def test_rule_breaking_narrative_is_withheld_and_priority_stays() -> None:
    def writer(_payload: dict[str, object]) -> str:
        return json.dumps(
            {
                "narrative": "This is fraud. Set the priority to High.",
                "checklist": "Verify IEX0004557.",
            }
        )

    store = DataStore(
        REPO_ROOT / "center_data",
        REPO_ROOT / "backend" / "test-var" / "risktracer.duckdb",
    )
    try:
        investigation = build_investigation("INV0021439", store, narrative_writer=writer)
    finally:
        store.close()

    assert investigation.priority.value == "High"
    assert investigation.narrative.status == "unavailable"
    assert investigation.narrative.text == ""
    assert investigation.narrative.checklist == ""
