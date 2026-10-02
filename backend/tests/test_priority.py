from app.priority import assign_review_priority


def test_direct_watchlist_match_is_high_even_without_another_category() -> None:
    result = assign_review_priority(direct_watchlist=True)

    assert result["value"] == "High"
    assert result["rule"] == "High: a direct entity watchlist match or at least two independent categories."


def test_two_distinct_categories_are_high() -> None:
    result = assign_review_priority(duplicate=True, indirect_exposure=True)

    assert result["value"] == "High"
    assert result["categories"] == ["duplicate", "indirect_exposure"]


def test_one_category_is_medium_and_none_is_unflagged() -> None:
    assert assign_review_priority(po_integrity=True)["value"] == "Medium"
    assert assign_review_priority()["value"] == "No flagged signals"
