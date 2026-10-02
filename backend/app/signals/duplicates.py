"""Possible duplicate submission detection."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

import pandas as pd
from rapidfuzz.fuzz import ratio


def normalize_invoice_number(value: Any) -> str:
    """Normalize the identifying portion of an invoice number."""

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return re.sub(r"[\s\-/_]+", "", str(value)).upper()


def _value(row: Mapping[str, Any] | pd.Series, key: str, default: Any = "") -> Any:
    value = row.get(key, default)
    if pd.isna(value):
        return default
    return value


def _amount(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _same_amount(left: Any, right: Any) -> bool:
    left_amount = _amount(left)
    right_amount = _amount(right)
    return (
        left_amount is not None
        and right_amount is not None
        and math.isclose(left_amount, right_amount, rel_tol=0, abs_tol=0.01)
    )


def _first_payment(invoice_id: str, payments: pd.DataFrame | None) -> dict[str, Any] | None:
    if payments is None or payments.empty or "invoice_id" not in payments.columns:
        return None
    matches = payments[payments["invoice_id"].astype(str) == invoice_id]
    if matches.empty:
        return None
    record = matches.iloc[0].to_dict()
    return {key: value for key, value in record.items() if not pd.isna(value)}


def find_possible_duplicates(
    invoice: Mapping[str, Any] | pd.Series,
    invoices: pd.DataFrame,
    payments: pd.DataFrame | None = None,
) -> list[dict[str, Any]]:
    """Return same-supplier, same-currency invoice records warranting comparison.

    Exact normalized invoice numbers match without an amount condition. Fuzzy
    matches require both a score of at least 90 and the same gross amount.
    """

    if invoices.empty:
        return []

    invoice_id = str(_value(invoice, "invoice_id"))
    supplier_id = str(_value(invoice, "supplier_id"))
    currency = str(_value(invoice, "currency"))
    normalized_number = normalize_invoice_number(_value(invoice, "invoice_number"))
    candidates = invoices[
        (invoices["invoice_id"].astype(str) != invoice_id)
        & (invoices["supplier_id"].astype(str) == supplier_id)
        & (invoices["currency"].astype(str) == currency)
    ]

    results: list[dict[str, Any]] = []
    for _, candidate in candidates.iterrows():
        candidate_number = normalize_invoice_number(_value(candidate, "invoice_number"))
        if not normalized_number or not candidate_number:
            continue

        exact = normalized_number == candidate_number
        score = 100.0 if exact else float(ratio(normalized_number, candidate_number))
        same_amount = _same_amount(
            _value(invoice, "gross_amount"), _value(candidate, "gross_amount")
        )
        if not exact and (score < 90 or not same_amount):
            continue

        matched_fields = ["invoice_number"] if exact else ["invoice_number_similarity", "gross_amount"]
        result = {
            "invoice_id": str(_value(candidate, "invoice_id")),
            "invoice_number": str(_value(candidate, "invoice_number")),
            "gross_amount": _amount(_value(candidate, "gross_amount")),
            "currency": currency,
            "matched_fields": matched_fields,
            "score": round(score, 2),
            "status": str(_value(candidate, "status")),
            "payment": _first_payment(str(_value(candidate, "invoice_id")), payments),
        }
        results.append(result)

    return sorted(results, key=lambda match: (-match["score"], match["invoice_id"]))
