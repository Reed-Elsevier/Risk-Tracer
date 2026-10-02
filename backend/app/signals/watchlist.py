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
    latest_by_entity: dict[str, dict[str, Any]] = {}
    for _, row in rows.iterrows():
        record = _record(row)
        entity_id = str(record.get("entity_id", ""))
        current = latest_by_entity.get(entity_id)
        candidate_key = (
            str(record.get("listed_date", "")),
            str(record.get("watchlist_entry_id", "")),
        )
        current_key = (
            str(current.get("listed_date", "")),
            str(current.get("watchlist_entry_id", "")),
        ) if current else ("", "")
        if current is None or candidate_key > current_key:
            latest_by_entity[entity_id] = record
    return sorted(latest_by_entity.values(), key=lambda item: str(item.get("entity_id", "")))


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

    watchlist_by_entity = {
        str(item.get("entity_id")): item for item in entity_watchlists
    }
    exposures: list[dict[str, Any]] = []

    def walk_upstream(
        current_entity_id: str,
        links_from_supplier: list[dict[str, Any]],
        visited: set[str],
    ) -> None:
        if len(links_from_supplier) >= 2:
            return
        for parent_entity_id, _, link_key in graph.in_edges(
            current_entity_id, keys=True
        ):
            parent_entity_id = str(parent_entity_id)
            if parent_entity_id in visited:
                continue
            link = dict(graph.edges[parent_entity_id, current_entity_id, link_key])
            next_links = links_from_supplier + [link]
            watchlist = watchlist_by_entity.get(parent_entity_id)
            if watchlist and parent_entity_id != str(entity_id):
                exposures.append(
                    {
                        "hop_count": len(next_links),
                        "entity_ids": [str(entity_id)]
                        + [str(item["parent_entity_id"]) for item in next_links],
                        "links": next_links,
                        "watchlist": dict(watchlist),
                    }
                )
            if (
                len(next_links) < 2
                and str(link.get("link_type", "")).casefold() != "indirect"
            ):
                walk_upstream(
                    parent_entity_id,
                    next_links,
                    visited | {parent_entity_id},
                )

    walk_upstream(str(entity_id), [], {str(entity_id)})

    exposures.sort(
        key=lambda item: (
            item["hop_count"],
            str(item["watchlist"].get("watchlist_entry_id", "")),
            [str(link.get("ownership_link_id", "")) for link in item["links"]],
        )
    )
    return {"direct_match": direct_match, "exposures": exposures}
