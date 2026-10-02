import pandas as pd

from app.signals.watchlist import find_watchlist_exposures


def test_watchlist_exposure_returns_two_upstream_links_from_supplier_outward() -> None:
    ownership_links = pd.DataFrame(
        [
            {
                "ownership_link_id": "OWN0009353",
                "parent_entity_id": "ENT002316",
                "child_entity_id": "ENT000140",
                "ownership_pct": "44.3",
                "link_type": "Nominee",
                "effective_date": "2020-07-03 00:00:00",
            },
            {
                "ownership_link_id": "OWN0003041",
                "parent_entity_id": "ENT007185",
                "child_entity_id": "ENT002316",
                "ownership_pct": "12.3",
                "link_type": "Direct",
                "effective_date": "2011-01-29 00:00:00",
            },
        ]
    )
    watchlists = pd.DataFrame(
        [
            {
                "watchlist_entry_id": "WL003070",
                "subject_type": "Entity",
                "entity_id": "ENT007185",
                "list_type": "Sanctions-like",
                "list_source": "Global Restricted Parties List (fictional)",
                "listed_date": "2017-08-24 00:00:00",
                "reason": "Asset freeze",
            }
        ]
    )

    result = find_watchlist_exposures("ENT000140", ownership_links, watchlists)

    assert result["direct_match"] is None
    assert len(result["exposures"]) == 1
    exposure = result["exposures"][0]
    assert exposure["hop_count"] == 2
    assert [link["ownership_link_id"] for link in exposure["links"]] == [
        "OWN0009353",
        "OWN0003041",
    ]
    assert exposure["watchlist"]["watchlist_entry_id"] == "WL003070"


def test_individual_watchlist_rows_are_not_treated_as_entity_exposure() -> None:
    watchlists = pd.DataFrame(
        [
            {
                "watchlist_entry_id": "WL001",
                "subject_type": "Individual",
                "entity_id": "",
            }
        ]
    )

    result = find_watchlist_exposures("ENT000140", pd.DataFrame(), watchlists)

    assert result == {"direct_match": None, "exposures": []}


def test_latest_entity_watchlist_record_is_used() -> None:
    watchlists = pd.DataFrame(
        [
            {
                "watchlist_entry_id": "WL001",
                "subject_type": "Entity",
                "entity_id": "ENT000140",
                "list_type": "Old list",
                "list_source": "Source",
                "listed_date": "2020-01-01 00:00:00",
                "reason": "Old reason",
            },
            {
                "watchlist_entry_id": "WL002",
                "subject_type": "Entity",
                "entity_id": "ENT000140",
                "list_type": "Latest list",
                "list_source": "Source",
                "listed_date": "2024-01-01 00:00:00",
                "reason": "Latest reason",
            },
        ]
    )

    result = find_watchlist_exposures("ENT000140", pd.DataFrame(), watchlists)

    assert result["direct_match"]["watchlist_entry_id"] == "WL002"


def test_indirect_link_is_a_terminal_recorded_link() -> None:
    ownership_links = pd.DataFrame(
        [
            {
                "ownership_link_id": "OWN001",
                "parent_entity_id": "ENT_PARENT",
                "child_entity_id": "ENT_SUPPLIER",
                "ownership_pct": "10",
                "link_type": "Indirect",
                "effective_date": "2020-01-01 00:00:00",
            },
            {
                "ownership_link_id": "OWN002",
                "parent_entity_id": "ENT_LISTED",
                "child_entity_id": "ENT_PARENT",
                "ownership_pct": "20",
                "link_type": "Direct",
                "effective_date": "2020-01-01 00:00:00",
            },
        ]
    )
    watchlists = pd.DataFrame(
        [
            {
                "watchlist_entry_id": "WL001",
                "subject_type": "Entity",
                "entity_id": "ENT_LISTED",
                "list_type": "Sanctions-like",
                "list_source": "Source",
                "listed_date": "2024-01-01 00:00:00",
                "reason": "Asset freeze",
            }
        ]
    )

    result = find_watchlist_exposures("ENT_SUPPLIER", ownership_links, watchlists)

    assert result["exposures"] == []
