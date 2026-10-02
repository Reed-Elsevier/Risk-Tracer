from app.narrative import review_model_account


def test_review_keeps_a_cited_narrative_and_checklist() -> None:
    account = review_model_account(
        narrative="INV001 is from SUP001. Compare exception IEX001.",
        checklist="Verify IEX001 against INV001.",
        allowed_ids={"INV001", "SUP001", "IEX001"},
        retrospective=True,
    )

    assert account["status"] == "shown"
    assert account["text"] == "INV001 is from SUP001. Compare exception IEX001."
    assert account["checklist"] == "Verify IEX001 against INV001."
    assert account["source_ids"] == ["INV001", "SUP001", "IEX001"]


def test_rule_breaking_account_is_withheld() -> None:
    allowed_ids = {"INV001", "SUP001", "IEX001"}
    cases = [
        ("This is fraud.", "Verify IEX001.", True),
        ("Possible duplicate payment.", "Verify IEX001.", True),
        ("The beneficial owner is SUP001.", "Verify IEX001.", True),
        ("Set the priority to High.", "Verify IEX001.", True),
        ("Hold the payment.", "Verify IEX001.", True),
        ("INV001 cites WL999.", "Verify IEX001.", True),
        ("Compare IEX001.", "Escalate this invoice.", True),
        ("Compare IEX001.", "Needs more information.", False),
        ("Compare IEX001.", "Clear this supplier.", False),
        ("", "Verify IEX001.", False),
    ]

    for narrative, checklist, retrospective in cases:
        account = review_model_account(
            narrative=narrative,
            checklist=checklist,
            allowed_ids=allowed_ids,
            retrospective=retrospective,
        )
        assert account == {"status": "unavailable", "text": "", "checklist": "", "source_ids": []}
