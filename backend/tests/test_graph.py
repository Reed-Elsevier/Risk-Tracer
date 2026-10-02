import pandas as pd

from app.graph import build_ownership_graph


def test_ownership_graph_marks_listed_entity_and_labels_recorded_links() -> None:
    graph = build_ownership_graph(
        supplier_entity_id="ENT000140",
        ownership_links=pd.DataFrame(
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
        ),
        entities=pd.DataFrame(
            [
                {"entity_id": "ENT000140", "legal_name": "Supplier Entity"},
                {"entity_id": "ENT002316", "legal_name": "Nominee Entity"},
                {"entity_id": "ENT007185", "legal_name": "Listed Entity"},
            ]
        ),
        watchlists=pd.DataFrame(
            [
                {
                    "watchlist_entry_id": "WL003070",
                    "subject_type": "Entity",
                    "entity_id": "ENT007185",
                }
            ]
        ),
    )

    assert {node["id"] for node in graph["nodes"]} == {
        "ENT000140",
        "ENT002316",
        "ENT007185",
    }
    assert next(node for node in graph["nodes"] if node["id"] == "ENT007185")["listed"] is True
    assert {edge["ownership_link_id"] for edge in graph["edges"]} == {
        "OWN0009353",
        "OWN0003041",
    }
