from app.brief import build_evidence_brief


def test_evidence_brief_cites_sources_and_uses_retrospective_language() -> None:
    brief = build_evidence_brief(
        invoice={
            "invoice_id": "INV001",
            "supplier_id": "SUP001",
            "currency": "PHP",
            "gross_amount": "165046.41",
            "status": "Paid",
        },
        supplier={"supplier_id": "SUP001", "supplier_name": "Torvale Technologies B.V."},
        duplicate_matches=[
            {
                "invoice_id": "INV002",
                "gross_amount": 165046.41,
                "currency": "PHP",
                "status": "Paid",
                "payment": {"payment_id": "PAY001"},
            }
        ],
        po_reasons=[],
        purchase_order={"po_id": "PO001"},
        watchlist={"direct_match": None, "exposures": []},
        exceptions=[{"exception_id": "IEX001", "exception_type": "Missing goods receipt"}],
        payment={"payment_id": "PAY002"},
    )

    text = " ".join(sentence["text"] for sentence in brief["sentences"])
    source_ids = {source_id for sentence in brief["sentences"] for source_id in sentence["source_ids"]}

    assert brief["retrospective"] is True
    assert "follow-up and verification" in brief["suggested_next_step"].lower()
    assert {"INV001", "INV002", "PAY001", "PAY002", "IEX001"} <= source_ids
    assert "fraud score" not in text.lower()
    assert "duplicate payment" not in text.lower()
    assert "beneficial owner" not in text.lower()


def test_exact_invoice_number_match_does_not_claim_amount_was_a_match_condition() -> None:
    brief = build_evidence_brief(
        invoice={"invoice_id": "INV001", "currency": "PHP", "gross_amount": "10", "status": "Approved"},
        supplier={"supplier_id": "SUP001", "supplier_name": "Supplier"},
        duplicate_matches=[
            {
                "invoice_id": "INV002",
                "gross_amount": 99,
                "currency": "PHP",
                "status": "Approved",
                "matched_fields": ["invoice_number"],
            }
        ],
        po_reasons=[],
        purchase_order=None,
        watchlist={"direct_match": None, "exposures": []},
        exceptions=[],
        payment=None,
    )

    duplicate_sentence = next(
        sentence["text"]
        for sentence in brief["sentences"]
        if "Possible duplicate submission" in sentence["text"]
    )
    assert "same normalized invoice number" in duplicate_sentence
    assert "gross amount" not in duplicate_sentence
