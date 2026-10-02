"""Counts and example records from one supplier's other invoices."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value)


def _unresolved(value: Any) -> bool:
    return pd.isna(value) or _text(value) == ""


def _recent_first(frame: pd.DataFrame) -> pd.DataFrame:
    ordered = frame.copy()
    ordered["_raised_at"] = ordered["raised_at"].map(_text)
    ordered["_exception_id"] = ordered["exception_id"].map(_text)
    return ordered.sort_values(
        ["_raised_at", "_exception_id"],
        ascending=[False, False],
        kind="mergesort",
    )


def summarize_supplier_history(
    *,
    supplier_id: str,
    current_invoice_id: str,
    invoices: pd.DataFrame,
    exceptions: pd.DataFrame,
) -> dict[str, Any]:
    """Count the supplier's other invoices and cap the example exceptions."""

    if invoices.empty:
        other_invoice_ids: set[str] = set()
    else:
        same_supplier = invoices[invoices["supplier_id"].astype(str) == str(supplier_id)]
        other_invoice_ids = {
            str(invoice_id)
            for invoice_id in same_supplier["invoice_id"].tolist()
            if str(invoice_id) != str(current_invoice_id)
        }

    if exceptions.empty or not other_invoice_ids:
        history = exceptions.iloc[0:0]
    else:
        history = exceptions[exceptions["invoice_id"].astype(str).isin(other_invoice_ids)]

    counts: list[dict[str, Any]] = []
    if not history.empty:
        for exception_type, group in history.groupby(history["exception_type"].astype(str), sort=True):
            unresolved = int(group["resolved_at"].map(_unresolved).sum())
            counts.append(
                {
                    "exception_type": str(exception_type),
                    "unresolved": unresolved,
                    "resolved": int(len(group) - unresolved),
                }
            )

    current_types: list[str] = []
    if not exceptions.empty:
        current = exceptions[exceptions["invoice_id"].astype(str) == str(current_invoice_id)]
        current_types = sorted({str(value) for value in current["exception_type"].tolist()})

    ordered_ids: list[str] = []
    seen: set[str] = set()

    def add(ids: list[str]) -> None:
        for exception_id in ids:
            if exception_id and exception_id not in seen:
                seen.add(exception_id)
                ordered_ids.append(exception_id)

    if not history.empty:
        for exception_type, _count in ((row["exception_type"], row) for row in counts):
            group = history[history["exception_type"].astype(str) == exception_type]
            unresolved = group[group["resolved_at"].map(_unresolved)]
            pool = unresolved if not unresolved.empty else group
            add([_text(_recent_first(pool).iloc[0]["exception_id"])])

        add([_text(value) for value in _recent_first(history)["exception_id"].head(5).tolist()])

        for exception_type in current_types:
            group = history[history["exception_type"].astype(str) == exception_type]
            if group.empty:
                continue
            add([_text(value) for value in _recent_first(group)["exception_id"].head(5).tolist()])

    return {
        "other_invoice_count": len(other_invoice_ids),
        "exception_counts": counts,
        "example_exception_ids": ordered_ids,
    }
