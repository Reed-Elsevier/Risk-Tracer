"""Ownership graph projection for the investigation UI."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _record(row: pd.Series) -> dict[str, Any]:
    return {key: value for key, value in row.to_dict().items() if not pd.isna(value)}


def _date(value: Any) -> str:
    return str(value).split(" ", 1)[0]


def build_ownership_graph(
    *,
    supplier_entity_id: str,
    ownership_links: pd.DataFrame,
    entities: pd.DataFrame,
    watchlists: pd.DataFrame,
) -> dict[str, list[dict[str, Any]]]:
    """Project the supplier and no more than two upstream link hops."""

    links_by_child: dict[str, list[dict[str, Any]]] = {}
    for _, row in ownership_links.iterrows():
        record = _record(row)
        child = str(record.get("child_entity_id", ""))
        parent = str(record.get("parent_entity_id", ""))
        if child and parent and record.get("ownership_link_id"):
            links_by_child.setdefault(child, []).append(record)
    for records in links_by_child.values():
        records.sort(key=lambda record: str(record.get("ownership_link_id", "")))

    selected_links: dict[str, dict[str, Any]] = {}
    depths = {supplier_entity_id: 0}
    frontier = [supplier_entity_id]
    for depth in range(2):
        next_frontier: list[str] = []
        for child in frontier:
            for link in links_by_child.get(child, []):
                parent = str(link["parent_entity_id"])
                link_id = str(link["ownership_link_id"])
                if link_id in selected_links:
                    continue
                selected_links[link_id] = link
                if parent not in depths:
                    depths[parent] = depth + 1
                    next_frontier.append(parent)
        frontier = next_frontier

    entity_records = {
        str(row.get("entity_id")): row
        for _, raw_row in entities.iterrows()
        if (row := _record(raw_row)).get("entity_id")
    }
    listed_records: dict[str, dict[str, Any]] = {}
    if not watchlists.empty and "subject_type" in watchlists.columns:
        for _, raw_row in watchlists.iterrows():
            record = _record(raw_row)
            entity_id = str(record.get("entity_id", ""))
            if record.get("subject_type") == "Entity" and entity_id and entity_id not in listed_records:
                listed_records[entity_id] = record

    node_ids = set(depths)
    for link in selected_links.values():
        node_ids.add(str(link["parent_entity_id"]))
        node_ids.add(str(link["child_entity_id"]))
    nodes: list[dict[str, Any]] = []
    for entity_id in sorted(node_ids, key=lambda current: (depths.get(current, 99), current)):
        entity = entity_records.get(entity_id, {})
        listed = entity_id in listed_records
        if entity_id == supplier_entity_id:
            kind = "supplier_entity"
        elif listed:
            kind = "listed_entity"
        else:
            kind = "upstream_entity"
        nodes.append(
            {
                "id": entity_id,
                "label": str(entity.get("legal_name", entity_id)),
                "kind": kind,
                "entity_id": entity_id,
                "listed": listed,
                "watchlist_entry_id": listed_records.get(entity_id, {}).get("watchlist_entry_id"),
            }
        )

    edges = []
    for link_id, link in sorted(selected_links.items()):
        pct = link.get("ownership_pct", "")
        try:
            pct_text = f"{float(pct):g}%"
        except (TypeError, ValueError):
            pct_text = f"{pct}%"
        edges.append(
            {
                "id": link_id,
                "source": str(link["parent_entity_id"]),
                "target": str(link["child_entity_id"]),
                "label": f"{link.get('link_type', 'Recorded')} · {pct_text} · {_date(link.get('effective_date', ''))}",
                "ownership_link_id": link_id,
            }
        )
    return {"nodes": nodes, "edges": edges}
