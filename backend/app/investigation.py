"""Assemble one deterministic investigation from source records and signals."""

from __future__ import annotations

from typing import Any

from app.brief import build_evidence_brief
from app.data import DataStore
from app.decisions import DecisionRepository
from app.graph import build_ownership_graph
from app.models import (
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
from app.signals.duplicates import find_possible_duplicates
from app.signals.po_integrity import find_po_integrity_reasons
from app.signals.watchlist import find_watchlist_exposures


class InvestigationNotFound(LookupError):
    """Raised when an invoice or its required supplier/entity is missing."""


def _model(model_type: type[Any], record: dict[str, Any] | None, label: str) -> Any:
    if record is None:
        raise InvestigationNotFound(label)
    return model_type.model_validate(record)


def build_investigation(
    invoice_id: str,
    store: DataStore,
    decisions: DecisionRepository | None = None,
    *,
    llm_available: bool = False,
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
        signals=Signals(
            duplicate=duplicate_signal,
            po_integrity=po_signal,
            watchlist=watchlist_signal,
            exceptions=exception_records,
        ),
        evidence_brief=brief_raw,
        graph=graph_raw,
        latest_decision=decisions.latest(invoice_id) if decisions else None,
        llm_available=llm_available,
    )
