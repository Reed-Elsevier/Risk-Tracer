import pandas as pd

from app.signals.duplicates import find_possible_duplicates


def test_possible_duplicate_matches_normalized_number_and_includes_payment() -> None:
    invoice = pd.Series(
        {
            "invoice_id": "INV001",
            "supplier_id": "SUP001",
            "currency": "PHP",
            "gross_amount": "165046.41",
            "invoice_number": "0409-2305-55877",
            "status": "On hold - exception",
        }
    )
    invoices = pd.DataFrame(
        [
            invoice.to_dict(),
            {
                "invoice_id": "INV002",
                "supplier_id": "SUP001",
                "currency": "PHP",
                "gross_amount": "165046.41",
                "invoice_number": "0409 / 2305 / 55877",
                "status": "Paid",
            },
            {
                "invoice_id": "INV003",
                "supplier_id": "SUP002",
                "currency": "PHP",
                "gross_amount": "165046.41",
                "invoice_number": "0409-2305-55877",
                "status": "Paid",
            },
        ]
    )
    payments = pd.DataFrame(
        [
            {
                "payment_id": "PAY001",
                "invoice_id": "INV002",
                "amount": "165046.41",
                "currency": "PHP",
            }
        ]
    )

    matches = find_possible_duplicates(invoice, invoices, payments)

    assert len(matches) == 1
    assert matches[0]["invoice_id"] == "INV002"
    assert matches[0]["matched_fields"] == ["invoice_number"]
    assert matches[0]["score"] == 100.0
    assert matches[0]["status"] == "Paid"
    assert matches[0]["payment"]["payment_id"] == "PAY001"
