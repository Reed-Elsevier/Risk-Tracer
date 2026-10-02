"""API and domain response models using RiskTracer glossary terminology."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class InvoiceRecord(DomainModel):
    invoice_id: str
    supplier_id: str
    po_id: str | None = None
    currency: str
    invoice_date: str
    net_amount: float
    tax_amount: float
    gross_amount: float
    amount_usd: float
    invoice_number: str
    received_at: str
    due_date: str
    approval_level: str
    channel: str
    ocr_confidence: float | None = None
    processor_employee_id: str
    status: str


class SupplierRecord(DomainModel):
    supplier_id: str
    entity_id: str
    supplier_name: str
    category: str
    country: str
    payment_terms_days: int
    risk_tier: str
    preferred: bool
    onboarded_date: str
    status: str


class PurchaseOrderRecord(DomainModel):
    po_id: str
    supplier_id: str
    cost_center_id: str
    requester_employee_id: str
    approver_employee_id: str
    po_date: str
    currency: str
    po_amount: float
    status: str


class PaymentRecord(DomainModel):
    payment_id: str
    invoice_id: str
    paid_at: str
    amount: float
    currency: str
    method: str
    payment_run_id: str
    days_vs_due: int


class ExceptionRecord(DomainModel):
    exception_id: str
    invoice_id: str
    exception_type: str
    raised_at: str
    resolved_at: str | None = None
    resolver_employee_id: str | None = None
    resolution: str | None = None


class BusinessEntityRecord(DomainModel):
    entity_id: str
    legal_name: str
    registration_number: str
    country: str
    industry: str
    entity_type: str
    incorporation_date: str
    employee_band: str
    annual_revenue_usd: float
    status: str
    is_listed: bool


class OwnershipLinkRecord(DomainModel):
    ownership_link_id: str
    parent_entity_id: str
    child_entity_id: str
    ownership_pct: float
    link_type: str
    effective_date: str


class WatchlistEntryRecord(DomainModel):
    watchlist_entry_id: str
    subject_type: str
    individual_id: str | None = None
    entity_id: str | None = None
    list_type: str
    list_source: str
    listed_date: str
    reason: str


class DuplicateMatch(DomainModel):
    invoice_id: str
    invoice_number: str
    gross_amount: float | None = None
    currency: str
    matched_fields: list[str]
    score: float
    status: str
    payment: PaymentRecord | None = None


class DuplicateSignal(DomainModel):
    category: Literal["duplicate"] = "duplicate"
    matches: list[DuplicateMatch] = Field(default_factory=list)


class POIntegrityReason(DomainModel):
    code: str
    label: str


class POIntegritySignal(DomainModel):
    category: Literal["po_integrity"] = "po_integrity"
    reasons: list[POIntegrityReason] = Field(default_factory=list)
    purchase_order: PurchaseOrderRecord | None = None


class WatchlistExposure(DomainModel):
    hop_count: int
    entity_ids: list[str]
    links: list[OwnershipLinkRecord]
    watchlist: WatchlistEntryRecord


class WatchlistSignal(DomainModel):
    direct_match: WatchlistEntryRecord | None = None
    exposures: list[WatchlistExposure] = Field(default_factory=list)


class Signals(DomainModel):
    duplicate: DuplicateSignal
    po_integrity: POIntegritySignal
    watchlist: WatchlistSignal
    exceptions: list[ExceptionRecord] = Field(default_factory=list)


class ReviewPriority(DomainModel):
    value: Literal["High", "Medium", "No flagged signals"]
    rule: str
    categories: list[str]
    direct_watchlist_match: bool = False


class EvidenceSentence(DomainModel):
    text: str
    source_ids: list[str] = Field(default_factory=list)


class EvidenceBrief(DomainModel):
    sentences: list[EvidenceSentence]
    suggested_next_step: str
    retrospective: bool


class GraphNode(DomainModel):
    id: str
    label: str
    kind: Literal["supplier_entity", "upstream_entity", "listed_entity"]
    entity_id: str
    listed: bool = False
    watchlist_entry_id: str | None = None


class GraphEdge(DomainModel):
    id: str
    source: str
    target: str
    label: str
    ownership_link_id: str


class OwnershipGraph(DomainModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ReviewDecision(DomainModel):
    decision_id: str
    invoice_id: str
    disposition: Literal["escalate", "clear", "needs_more_info"]
    note: str
    priority: str
    priority_override: str | None = None
    override_reason: str | None = None
    reviewer: str
    created_at: str
    evidence_snapshot: dict[str, Any]


class InvestigationNarrative(DomainModel):
    status: Literal["shown", "unavailable"]
    text: str = ""
    checklist: str = ""
    source_ids: list[str] = Field(default_factory=list)


class Investigation(DomainModel):
    invoice: InvoiceRecord
    supplier: SupplierRecord
    entity: BusinessEntityRecord
    payment: PaymentRecord | None = None
    priority: ReviewPriority
    signals: Signals
    evidence_brief: EvidenceBrief
    graph: OwnershipGraph
    narrative: InvestigationNarrative = Field(
        default_factory=lambda: InvestigationNarrative(status="unavailable")
    )
    latest_decision: ReviewDecision | None = None
    llm_available: bool = False


class InvestigationRequest(DomainModel):
    invoice_id: str = Field(min_length=1)


class DecisionRequest(DomainModel):
    disposition: Literal["escalate", "clear", "needs_more_info"]
    note: str = ""
    priority_override: Literal["High", "Medium", "No flagged signals"] | None = None
    override_reason: str | None = None
    reviewer: str = Field(min_length=1)
    narrative: InvestigationNarrative | None = None


class InvoiceSearchResult(DomainModel):
    invoice_id: str
    invoice_number: str
    supplier_id: str
    supplier_name: str
    gross_amount: float
    currency: str
    status: str


class ExplainResponse(DomainModel):
    narrative: str
    source_ids: list[str] = Field(default_factory=list)


class HealthResponse(DomainModel):
    status: Literal["ok"]
    invoices: int
