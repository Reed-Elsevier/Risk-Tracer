import pandas as pd

from app.supplier_history import summarize_supplier_history


def test_supplier_history_counts_other_invoices_and_caps_example_exceptions() -> None:
    invoices = pd.DataFrame(
        [
            {"invoice_id": "INV-CURRENT", "supplier_id": "SUP1"},
            {"invoice_id": "INV-A", "supplier_id": "SUP1"},
            {"invoice_id": "INV-B", "supplier_id": "SUP1"},
            {"invoice_id": "INV-OTHER", "supplier_id": "SUP2"},
        ]
    )
    exceptions = pd.DataFrame(
        [
            {"exception_id": "IEX-CURRENT", "invoice_id": "INV-CURRENT", "exception_type": "Missing PO", "raised_at": "2026-07-01", "resolved_at": None},
            {"exception_id": "IEX-B1", "invoice_id": "INV-A", "exception_type": "Bank details changed", "raised_at": "2026-03-01", "resolved_at": None},
            {"exception_id": "IEX-B2", "invoice_id": "INV-A", "exception_type": "Bank details changed", "raised_at": "2026-02-01", "resolved_at": "2026-02-02"},
            {"exception_id": "IEX-B3", "invoice_id": "INV-B", "exception_type": "Bank details changed", "raised_at": "2026-01-01", "resolved_at": None},
            {"exception_id": "IEX-T1", "invoice_id": "INV-A", "exception_type": "Tax error", "raised_at": "2026-05-01", "resolved_at": "2026-05-02"},
            {"exception_id": "IEX-T2", "invoice_id": "INV-B", "exception_type": "Tax error", "raised_at": "2026-04-01", "resolved_at": "2026-04-02"},
            {"exception_id": "IEX-M1", "invoice_id": "INV-A", "exception_type": "Missing PO", "raised_at": "2026-06-01", "resolved_at": None},
            {"exception_id": "IEX-M2", "invoice_id": "INV-A", "exception_type": "Missing PO", "raised_at": "2026-05-15", "resolved_at": None},
            {"exception_id": "IEX-M3", "invoice_id": "INV-B", "exception_type": "Missing PO", "raised_at": "2026-05-01", "resolved_at": None},
            {"exception_id": "IEX-M4", "invoice_id": "INV-A", "exception_type": "Missing PO", "raised_at": "2026-04-01", "resolved_at": None},
            {"exception_id": "IEX-M5", "invoice_id": "INV-B", "exception_type": "Missing PO", "raised_at": "2026-03-01", "resolved_at": None},
            {"exception_id": "IEX-M6", "invoice_id": "INV-A", "exception_type": "Missing PO", "raised_at": "2026-02-01", "resolved_at": None},
            {"exception_id": "IEX-X", "invoice_id": "INV-OTHER", "exception_type": "Tax error", "raised_at": "2026-08-01", "resolved_at": None},
        ]
    )

    summary = summarize_supplier_history(
        supplier_id="SUP1",
        current_invoice_id="INV-CURRENT",
        invoices=invoices,
        exceptions=exceptions,
    )

    assert summary["other_invoice_count"] == 2
    assert summary["exception_counts"] == [
        {"exception_type": "Bank details changed", "unresolved": 2, "resolved": 1},
        {"exception_type": "Missing PO", "unresolved": 6, "resolved": 0},
        {"exception_type": "Tax error", "unresolved": 0, "resolved": 2},
    ]
    assert summary["example_exception_ids"] == [
        "IEX-B1",
        "IEX-M1",
        "IEX-T1",
        "IEX-M2",
        "IEX-M3",
        "IEX-T2",
        "IEX-M4",
        "IEX-M5",
    ]
