"""Deterministic, source-cited evidence brief generation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def _amount(value: Any) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def build_evidence_brief(
    *,
    invoice: Mapping[str, Any],
    supplier: Mapping[str, Any],
    duplicate_matches: Sequence[Mapping[str, Any]],
    po_reasons: Sequence[Mapping[str, Any]],
    purchase_order: Mapping[str, Any] | None,
    watchlist: Mapping[str, Any],
    exceptions: Sequence[Mapping[str, Any]],
    payment: Mapping[str, Any] | None,
    entity: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a concise evidence brief without probabilistic conclusions."""

    invoice_id = str(invoice.get("invoice_id", ""))
    supplier_id = str(invoice.get("supplier_id", ""))
    currency = str(invoice.get("currency", ""))
    sentences: list[dict[str, Any]] = []
    sentences.append(
        {
            "text": (
                f"{invoice_id} is an invoice for {currency} {_amount(invoice.get('gross_amount'))} "
                f"from {supplier.get('supplier_name', supplier_id)}; its current status is "
                f"{invoice.get('status', 'unknown')}."
            ),
            "source_ids": [source for source in (invoice_id, supplier_id) if source],
        }
    )
    if payment and payment.get("payment_id"):
        sentences.append(
            {
                "text": f"Payment {payment.get('payment_id')} is recorded for this invoice.",
                "source_ids": [invoice_id, str(payment["payment_id"])],
            }
        )

    for match in duplicate_matches:
        candidate_id = str(match.get("invoice_id", ""))
        match_sources = [source for source in (invoice_id, candidate_id) if source]
        payment_record = match.get("payment")
        if payment_record and payment_record.get("payment_id"):
            match_sources.append(str(payment_record["payment_id"]))
        payment_text = ""
        if payment_record:
            payment_text = f"; payment {payment_record.get('payment_id')} is recorded"
        matched_fields = set(match.get("matched_fields", []))
        if "invoice_number_similarity" in matched_fields:
            match_description = "a similar normalized invoice number and the same gross amount"
        else:
            match_description = "the same normalized invoice number"
        sentences.append(
            {
                "text": (
                    f"Possible duplicate submission: {candidate_id} has {match_description} "
                    f"at {currency} {_amount(match.get('gross_amount'))}; its "
                    f"status is {match.get('status', 'unknown')}{payment_text}."
                ),
                "source_ids": list(dict.fromkeys(match_sources)),
            }
        )

    if po_reasons:
        reason_text = "; ".join(str(reason.get("label", reason.get("code", ""))) for reason in po_reasons)
        po_source = str(purchase_order.get("po_id")) if purchase_order and purchase_order.get("po_id") else None
        sources = [source for source in (invoice_id, po_source) if source]
        sentences.append(
            {
                "text": f"PO integrity signal: {reason_text}.",
                "source_ids": sources,
            }
        )
    elif purchase_order:
        sentences.append(
            {
                "text": (
                    f"Purchase order {purchase_order.get('po_id')} matches the invoice supplier "
                    f"and currency; no PO integrity signal was found."
                ),
                "source_ids": [source for source in (invoice_id, purchase_order.get("po_id")) if source],
            }
        )

    direct_match = watchlist.get("direct_match")
    if direct_match:
        direct_sources = [invoice_id, str(direct_match.get("watchlist_entry_id", ""))]
        if entity and entity.get("entity_id"):
            direct_sources.append(str(entity["entity_id"]))
        sentences.append(
            {
                "text": (
                    f"Direct entity watchlist match: entity {direct_match.get('entity_id')} is listed "
                    f"as {direct_match.get('list_type', 'watchlisted')} ({direct_match.get('reason', 'no reason recorded')}); "
                    f"listed date {str(direct_match.get('listed_date', ''))[:10]}."
                ),
                "source_ids": [source for source in direct_sources if source],
            }
        )

    for exposure in watchlist.get("exposures", []):
        exposure_watchlist = exposure.get("watchlist", {})
        links = exposure.get("links", [])
        link_ids = [str(link.get("ownership_link_id")) for link in links if link.get("ownership_link_id")]
        link_details = [
            f"{link.get('ownership_link_id')} ({str(link.get('effective_date', ''))[:10]})"
            for link in links
            if link.get("ownership_link_id")
        ]
        path_entity = exposure_watchlist.get("entity_id", "listed entity")
        sources = [
            str(path_entity),
            *link_ids,
            str(exposure_watchlist.get("watchlist_entry_id", "")),
        ]
        if entity and entity.get("entity_id"):
            sources.insert(0, str(entity["entity_id"]))
        sentences.append(
            {
                "text": (
                    f"Latest recorded exposure: the supplier entity is connected to listed entity "
                    f"{path_entity} through {', '.join(link_details)}; the listed record is "
                    f"{exposure_watchlist.get('watchlist_entry_id')} ({exposure_watchlist.get('list_type', 'watchlisted')}) "
                    f"with listed date {str(exposure_watchlist.get('listed_date', ''))[:10]}."
                ),
                "source_ids": [source for source in sources if source],
            }
        )

    for exception in exceptions:
        resolved = "resolved" if exception.get("resolved_at") else "unresolved"
        sentences.append(
            {
                "text": (
                    f"Invoice exception {exception.get('exception_id')}: "
                    f"{exception.get('exception_type')} ({resolved})."
                ),
                "source_ids": [source for source in (invoice_id, exception.get("exception_id")) if source],
            }
        )

    retrospective = bool(payment) or str(invoice.get("status", "")) == "Paid"
    suggested_next_step = (
        "Follow-up and verification of the recorded evidence is the next step because this is a retrospective review."
        if retrospective
        else "Complete the human review before payment processing proceeds."
    )
    return {
        "sentences": sentences,
        "suggested_next_step": suggested_next_step,
        "retrospective": retrospective,
    }
