import pandas as pd

from app.signals.po_integrity import find_po_integrity_reasons


def test_po_integrity_lists_each_independent_reason() -> None:
    invoice = pd.Series(
        {
            "invoice_id": "INV001",
            "supplier_id": "SUP001",
            "po_id": "PO001",
            "currency": "PHP",
        }
    )
    purchase_orders = pd.DataFrame(
        [
            {
                "po_id": "PO001",
                "supplier_id": "SUP002",
                "currency": "USD",
            }
        ]
    )

    reasons = find_po_integrity_reasons(invoice, purchase_orders)

    assert [reason["code"] for reason in reasons] == [
        "po_supplier_mismatch",
        "po_currency_mismatch",
    ]


def test_missing_po_reference_is_a_signal() -> None:
    invoice = pd.Series(
        {"invoice_id": "INV002", "supplier_id": "SUP001", "po_id": "", "currency": "PHP"}
    )

    reasons = find_po_integrity_reasons(invoice, pd.DataFrame())

    assert reasons == [{"code": "missing_po_reference", "label": "Missing purchase order reference"}]
