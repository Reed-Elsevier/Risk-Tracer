"""Assemble one deterministic investigation from source records and signals."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from app.brief import build_evidence_brief
from app.data import DataStore
from app.decisions import DecisionRepository
from app.graph import build_ownership_graph
from app.narrative import review_model_account
from app.models import (
    InvestigationNarrative,
    BusinessEntityRecord,
    DuplicateSignal,
    ExceptionRecord,
    Investigation,
    InvoiceRecord,
    POIntegritySignal,
    PaymentRecord,
    PurchaseOrderRecord,
    ReviewPriority,
    Signals,
    SupplierRecord,
    WatchlistSignal,
)
from app.priority import assign_review_priority
from app.supplier_history import summarize_supplier_history
from app.signals.duplicates import find_possible_duplicates
from app.signals.po_integrity import find_po_integrity_reasons
from app.signals.watchlist import find_watchlist_exposures


class InvestigationNotFound(LookupError):
    """Raised when an invoice or its required supplier/entity is missing."""


def _model(model_type: type[Any], record: dict[str, Any] | None, label: str) -> Any:
    if record is None:
        raise InvestigationNotFound(label)
    return model_type.model_validate(record)


NarrativeWriter = Callable[[dict[str, Any]], str]


def _unavailable_narrative() -> InvestigationNarrative:
    return InvestigationNarrative(status="unavailable")


def _example_records(exception_ids: list[str], exceptions: Any) -> list[dict[str, str]]:
    if not exception_ids or exceptions.empty:
        return []
    matched = exceptions[exceptions["exception_id"].astype(str).isin(exception_ids)]
    by_id = {str(row["exception_id"]): row for _, row in matched.iterrows()}
    records: list[dict[str, str]] = []
    for exception_id in exception_ids:
        row = by_id.get(exception_id)
        if row is None:
            continue
        records.append(
            {
                "exception_id": exception_id,
                "invoice_id": str(row["invoice_id"]),
                "exception_type": str(row["exception_type"]),
            }
        )
    return records


def _narrative_for(
    *,
    invoice_raw: dict[str, Any],
    supplier_raw: dict[str, Any],
    entity_raw: dict[str, Any],
    signals: Signals,
    brief_raw: dict[str, Any],
    store: DataStore,
    narrative_writer: NarrativeWriter | None,
) -> InvestigationNarrative:
    if narrative_writer is None:
        return _unavailable_narrative()

    summary = summarize_supplier_history(
        supplier_id=str(invoice_raw.get("supplier_id", "")),
        current_invoice_id=str(invoice_raw.get("invoice_id", "")),
        invoices=store.frames["invoices"],
        exceptions=store.frames["invoice_exceptions"],
    )
    examples = _example_records(summary["example_exception_ids"], store.frames["invoice_exceptions"])
    allowed_ids = {
        source_id
        for sentence in brief_raw["sentences"]
        for source_id in sentence["source_ids"]
    }
    for example in examples:
        allowed_ids.add(example["exception_id"])
        allowed_ids.add(example["invoice_id"])
    payload = {
        "invoice": invoice_raw,
        "supplier": supplier_raw,
        "entity": entity_raw,
        "signals": signals.model_dump(mode="json"),
        "evidence_brief": brief_raw,
        "supplier_history": {
            "other_invoice_count": summary["other_invoice_count"],
            "exception_counts": summary["exception_counts"],
            "examples": examples,
        },
        "allowed_source_ids": sorted(allowed_ids),
    }
    try:
        parsed = json.loads(narrative_writer(payload))
        account = review_model_account(
            narrative=str(parsed.get("narrative", "")),
            checklist=str(parsed.get("checklist", "")),
            allowed_ids=allowed_ids,
            retrospective=bool(brief_raw["retrospective"]),
        )
    except Exception:
        return _unavailable_narrative()
    return InvestigationNarrative.model_validate(account)


def apply_submitted_narrative(
    investigation: Investigation,
    store: DataStore,
    submission: InvestigationNarrative,
) -> Investigation:
    """Keep the narrative the reviewer saw, without calling the model again."""

    if submission.status != "shown":
        return investigation.model_copy(update={"narrative": _unavailable_narrative()})
    invoice_raw = investigation.invoice.model_dump(mode="json")
    brief_raw = investigation.evidence_brief.model_dump(mode="json")
    summary = summarize_supplier_history(
        supplier_id=str(invoice_raw.get("supplier_id", "")),
        current_invoice_id=str(invoice_raw.get("invoice_id", "")),
        invoices=store.frames["invoices"],
        exceptions=store.frames["invoice_exceptions"],
    )
    examples = _example_records(summary["example_exception_ids"], store.frames["invoice_exceptions"])
    allowed_ids = {
        source_id
        for sentence in brief_raw["sentences"]
        for source_id in sentence["source_ids"]
    }
    for example in examples:
        allowed_ids.add(example["exception_id"])
        allowed_ids.add(example["invoice_id"])
    account = review_model_account(
        narrative=submission.text,
        checklist=submission.checklist,
        allowed_ids=allowed_ids,
        retrospective=investigation.evidence_brief.retrospective,
    )
    return investigation.model_copy(update={"narrative": InvestigationNarrative.model_validate(account)})


def build_investigation(
    invoice_id: str,
    store: DataStore,
    decisions: DecisionRepository | None = None,
    *,
    llm_available: bool = False,
    narrative_writer: NarrativeWriter | None = None,
) -> Investigation:
    invoice_raw = store.invoice(invoice_id)
    invoice = _model(InvoiceRecord, invoice_raw, f"Invoice {invoice_id} not found")
    supplier_raw = store.supplier(invoice.supplier_id)
    supplier = _model(SupplierRecord, supplier_raw, f"Supplier {invoice.supplier_id} not found")
    entity_raw = store.entity(supplier.entity_id)
    entity = _model(BusinessEntityRecord, entity_raw, f"Entity {supplier.entity_id} not found")

    duplicate_matches = find_possible_duplicates(
        invoice_raw or {}, store.frames["invoices"], store.frames["payments"]
    )
    duplicate_signal = DuplicateSignal(matches=duplicate_matches)

    po_reasons = find_po_integrity_reasons(invoice_raw or {}, store.frames["purchase_orders"])
    purchase_order_raw = store.purchase_order(invoice.po_id)
    po_signal = POIntegritySignal(
        reasons=po_reasons,
        purchase_order=(
            PurchaseOrderRecord.model_validate(purchase_order_raw)
            if purchase_order_raw
            else None
        ),
    )

    watchlist_raw = find_watchlist_exposures(
        entity.entity_id,
        store.frames["ownership_links"],
        store.frames["watchlists"],
    )
    watchlist_signal = WatchlistSignal.model_validate(watchlist_raw)
    exception_records = [ExceptionRecord.model_validate(record) for record in store.exceptions(invoice_id)]
    payment_raw = store.payment(invoice_id)
    payment = PaymentRecord.model_validate(payment_raw) if payment_raw else None

    priority_raw = assign_review_priority(
        duplicate=bool(duplicate_signal.matches),
        indirect_exposure=bool(watchlist_signal.exposures),
        po_integrity=bool(po_signal.reasons),
        direct_watchlist=bool(watchlist_signal.direct_match),
    )
    priority = ReviewPriority.model_validate(priority_raw)
    signals = Signals(
        duplicate=duplicate_signal,
        po_integrity=po_signal,
        watchlist=watchlist_signal,
        exceptions=exception_records,
    )
    brief_raw = build_evidence_brief(
        invoice=invoice_raw or {},
        supplier=supplier_raw or {},
        duplicate_matches=duplicate_matches,
        po_reasons=po_reasons,
        purchase_order=purchase_order_raw,
        watchlist=watchlist_raw,
        exceptions=store.exceptions(invoice_id),
        payment=payment_raw,
        entity=entity_raw,
    )
    graph_raw = build_ownership_graph(
        supplier_entity_id=entity.entity_id,
        ownership_links=store.frames["ownership_links"],
        entities=store.frames["business_entities"],
        watchlists=store.frames["watchlists"],
    )
    return Investigation(
        invoice=invoice,
        supplier=supplier,
        entity=entity,
        payment=payment,
        priority=priority,
        signals=signals,
        evidence_brief=brief_raw,
        graph=graph_raw,
        narrative=_narrative_for(
            invoice_raw=invoice_raw or {},
            supplier_raw=supplier_raw or {},
            entity_raw=entity_raw or {},
            signals=signals,
            brief_raw=brief_raw,
            store=store,
            narrative_writer=narrative_writer,
        ),
        latest_decision=decisions.latest(invoice_id) if decisions else None,
        llm_available=llm_available,
    )
