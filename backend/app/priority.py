"""ADR-0002 review priority rules."""

from __future__ import annotations


HIGH_RULE = "High: a direct entity watchlist match or at least two independent categories."
MEDIUM_RULE = "Medium: exactly one signal category."
NONE_RULE = "No flagged signals: no signal categories."


def assign_review_priority(
    *,
    duplicate: bool = False,
    indirect_exposure: bool = False,
    po_integrity: bool = False,
    direct_watchlist: bool = False,
) -> dict[str, object]:
    """Assign the reproducible initial review priority from signal categories."""

    categories = [
        category
        for category, present in (
            ("duplicate", duplicate),
            ("indirect_exposure", indirect_exposure),
            ("po_integrity", po_integrity),
        )
        if present
    ]
    if direct_watchlist or len(categories) >= 2:
        return {
            "value": "High",
            "rule": HIGH_RULE,
            "categories": categories,
            "direct_watchlist_match": direct_watchlist,
        }
    if categories:
        return {
            "value": "Medium",
            "rule": MEDIUM_RULE,
            "categories": categories,
            "direct_watchlist_match": direct_watchlist,
        }
    return {
        "value": "No flagged signals",
        "rule": NONE_RULE,
        "categories": [],
        "direct_watchlist_match": direct_watchlist,
    }
