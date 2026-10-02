"""Purchase-order integrity checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd


REASON_LABELS = {
    "missing_po_reference": "Missing purchase order reference",
    "po_not_found": "Referenced purchase order was not found",
    "po_supplier_mismatch": "Purchase order supplier differs from invoice supplier",
    "po_currency_mismatch": "Purchase order currency differs from invoice currency",
}


def _value(row: Mapping[str, Any] | pd.Series, key: str, default: Any = "") -> Any:
    value = row.get(key, default)
    return default if pd.isna(value) else value


def find_po_integrity_reasons(
    invoice: Mapping[str, Any] | pd.Series,
    purchase_orders: pd.DataFrame,
) -> list[dict[str, str]]:
    """Return every independently applicable PO integrity reason."""

    po_id = str(_value(invoice, "po_id")).strip()
    if not po_id:
        return [
            {"code": "missing_po_reference", "label": REASON_LABELS["missing_po_reference"]}
        ]

    if purchase_orders.empty or "po_id" not in purchase_orders.columns:
        return [{"code": "po_not_found", "label": REASON_LABELS["po_not_found"]}]

    matches = purchase_orders[purchase_orders["po_id"].astype(str) == po_id]
    if matches.empty:
        return [{"code": "po_not_found", "label": REASON_LABELS["po_not_found"]}]

    purchase_order = matches.iloc[0]
    reasons: list[dict[str, str]] = []
    if str(_value(purchase_order, "supplier_id")) != str(_value(invoice, "supplier_id")):
        reasons.append(
            {"code": "po_supplier_mismatch", "label": REASON_LABELS["po_supplier_mismatch"]}
        )
    if str(_value(purchase_order, "currency")) != str(_value(invoice, "currency")):
        reasons.append(
            {"code": "po_currency_mismatch", "label": REASON_LABELS["po_currency_mismatch"]}
        )
    return reasons
