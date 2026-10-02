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
