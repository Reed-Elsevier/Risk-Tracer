"""Accept or withhold an investigation narrative and its checklist."""

from __future__ import annotations

import re
from typing import Any


SOURCE_ID_PATTERN = re.compile(r"\b(?:INV|PAY|OWN|WL|IEX|PO|SUP|ENT)\d+\b")
FORBIDDEN_LANGUAGE = re.compile(
    r"\b(?:fraud|priority|no flagged signals|escalate|needs more information|"
    r"duplicate payment|beneficial owner|clear this)\b",
    re.IGNORECASE,
)
HOLD_PAYMENT = re.compile(r"\bhold the payment\b", re.IGNORECASE)


def _cited_ids(*texts: str) -> list[str]:
    found: list[str] = []
    for text in texts:
        found.extend(SOURCE_ID_PATTERN.findall(text))
    return list(dict.fromkeys(found))


def review_model_account(
    *,
    narrative: str,
    checklist: str,
    allowed_ids: set[str],
    retrospective: bool,
) -> dict[str, Any]:
    """Return the account when every cited id was supplied."""

    combined = f"{narrative}\n{checklist}".strip()
    if not narrative.strip() or not checklist.strip():
        return {"status": "unavailable", "text": "", "checklist": "", "source_ids": []}
    if FORBIDDEN_LANGUAGE.search(combined):
        return {"status": "unavailable", "text": "", "checklist": "", "source_ids": []}
    if retrospective and HOLD_PAYMENT.search(combined):
        return {"status": "unavailable", "text": "", "checklist": "", "source_ids": []}
    cited_ids = _cited_ids(narrative, checklist)
    if any(source_id not in allowed_ids for source_id in cited_ids):
        return {"status": "unavailable", "text": "", "checklist": "", "source_ids": []}
    return {
        "status": "shown",
        "text": narrative.strip(),
        "checklist": checklist.strip(),
        "source_ids": cited_ids,
    }
