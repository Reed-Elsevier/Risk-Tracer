"""Exact entity watchlist matches and bounded upstream exposure."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import networkx as nx
import pandas as pd


def _record(row: Mapping[str, Any] | pd.Series) -> dict[str, Any]:
    record = row.to_dict() if isinstance(row, pd.Series) else dict(row)
    return {key: value for key, value in record.items() if not pd.isna(value)}


def _entity_watchlists(watchlists: pd.DataFrame) -> list[dict[str, Any]]:
    if watchlists.empty:
        return []
    rows = watchlists[
        (watchlists.get("subject_type", pd.Series(dtype=str)).astype(str) == "Entity")
        & watchlists.get("entity_id", pd.Series(dtype=str)).astype(str).ne("")
    ]
    return sorted(
        (_record(row) for _, row in rows.iterrows()),
        key=lambda item: (str(item.get("listed_date", "")), str(item.get("watchlist_entry_id", ""))),
    )


def find_watchlist_exposures(
    entity_id: str,
    ownership_links: pd.DataFrame,
    watchlists: pd.DataFrame,
) -> dict[str, Any]:
    """Find a direct match and at most two upstream recorded links.

    The returned link order starts at the supplier entity and moves upstream,
    so an evidence brief can cite the ownership path in reviewer reading order.
    """

    entity_watchlists = _entity_watchlists(watchlists)
    direct_match = next(
        (
            item
            for item in entity_watchlists
            if str(item.get("entity_id", "")) == str(entity_id)
        ),
        None,
    )
    if ownership_links.empty or not entity_watchlists:
        return {"direct_match": direct_match, "exposures": []}

    graph = nx.MultiDiGraph()
    for _, row in ownership_links.iterrows():
        record = _record(row)
        parent = str(record.get("parent_entity_id", ""))
        child = str(record.get("child_entity_id", ""))
        link_id = str(record.get("ownership_link_id", ""))
        if parent and child and link_id:
            graph.add_edge(parent, child, key=link_id, **record)

    exposures: list[dict[str, Any]] = []
    for watchlist in entity_watchlists:
        listed_entity_id = str(watchlist.get("entity_id", ""))
        if not listed_entity_id or listed_entity_id == str(entity_id):
            continue
        if listed_entity_id not in graph or str(entity_id) not in graph:
            continue
        try:
            edge_paths = nx.all_simple_edge_paths(
                graph, listed_entity_id, str(entity_id), cutoff=2
            )
        except nx.NetworkXNoPath:
            continue
        for edge_path in edge_paths:
            if not edge_path or len(edge_path) > 2:
                continue
            source_to_target_links = [
                dict(graph.edges[source, target, key])
                for source, target, key in edge_path
            ]
            exposures.append(
                {
                    "hop_count": len(edge_path),
                    "entity_ids": [listed_entity_id]
                    + [str(target) for _, target, _ in edge_path[:-1]]
                    + [str(entity_id)],
                    "links": list(reversed(source_to_target_links)),
                    "watchlist": dict(watchlist),
                }
            )

    exposures.sort(
        key=lambda item: (
            item["hop_count"],
            str(item["watchlist"].get("watchlist_entry_id", "")),
            [str(link.get("ownership_link_id", "")) for link in item["links"]],
        )
    )
    return {"direct_match": direct_match, "exposures": exposures}
