export type ReviewPriority = "High" | "Medium" | "No flagged signals";

export interface EvidenceSentence {
  text: string;
  source_ids: string[];
}

export interface ExplainResponse {
  narrative: string;
  source_ids: string[];
}

export interface Invoice {
  invoice_id: string;
  supplier_id: string;
  po_id: string | null;
  currency: string;
  invoice_date: string;
  net_amount: number;
  tax_amount: number;
  gross_amount: number;
  amount_usd: number;
  invoice_number: string;
  received_at: string;
  due_date: string;
  approval_level: string;
  channel: string;
  ocr_confidence: number | null;
  processor_employee_id: string;
  status: string;
}

export interface Supplier {
  supplier_id: string;
  entity_id: string;
  supplier_name: string;
  category: string;
  country: string;
  payment_terms_days: number;
  risk_tier: string;
  preferred: boolean;
  onboarded_date: string;
  status: string;
}

export interface SupplierProfile {
  supplier: Supplier;
  invoices: Invoice[];
}

export interface Payment {
  payment_id: string;
  invoice_id: string;
  paid_at: string;
  amount: number;
  currency: string;
  method: string;
  payment_run_id: string;
  days_vs_due: number;
}

export interface PurchaseOrder {
  po_id: string;
  supplier_id: string;
  cost_center_id: string;
  requester_employee_id: string;
  approver_employee_id: string;
  po_date: string;
  currency: string;
  po_amount: number;
  status: string;
}

export interface DuplicateMatch {
  invoice_id: string;
  invoice_number: string;
  gross_amount: number | null;
  currency: string;
  matched_fields: string[];
  score: number;
  status: string;
  payment: Payment | null;
}

export interface ExceptionRecord {
  exception_id: string;
  invoice_id: string;
  exception_type: string;
  raised_at: string;
  resolved_at: string | null;
  resolver_employee_id: string | null;
  resolution: string | null;
}

export interface POReason {
  code: string;
  label: string;
}

export interface OwnershipLink {
  ownership_link_id: string;
  parent_entity_id: string;
  child_entity_id: string;
  ownership_pct: number;
  link_type: string;
  effective_date: string;
}

export interface WatchlistEntry {
  watchlist_entry_id: string;
  subject_type: string;
  individual_id: string | null;
  entity_id: string | null;
  list_type: string;
  list_source: string;
  listed_date: string;
  reason: string;
}

export interface WatchlistExposure {
  hop_count: number;
  entity_ids: string[];
  links: OwnershipLink[];
  watchlist: WatchlistEntry;
}

export interface Investigation {
  invoice: Invoice;
  supplier: Supplier;
  entity: {
    entity_id: string;
    legal_name: string;
    country: string;
    industry: string;
    status: string;
    is_listed: boolean;
  };
  payment: Payment | null;
  priority: {
    value: ReviewPriority;
    rule: string;
    categories: string[];
    direct_watchlist_match: boolean;
  };
  signals: {
    duplicate: { matches: DuplicateMatch[] };
    po_integrity: { reasons: POReason[]; purchase_order: PurchaseOrder | null };
    watchlist: { direct_match: WatchlistEntry | null; exposures: WatchlistExposure[] };
    exceptions: ExceptionRecord[];
  };
  evidence_brief: {
    sentences: EvidenceSentence[];
    suggested_next_step: string;
    retrospective: boolean;
  };
  graph: {
    nodes: {
      id: string;
      label: string;
      kind: "supplier_entity" | "upstream_entity" | "listed_entity";
      entity_id: string;
      listed: boolean;
      watchlist_entry_id: string | null;
    }[];
    edges: {
      id: string;
      source: string;
      target: string;
      label: string;
      ownership_link_id: string;
    }[];
  };
  latest_decision: ReviewDecision | null;
  llm_available: boolean;
}

export interface ReviewDecision {
  decision_id: string;
  invoice_id: string;
  disposition: "escalate" | "clear" | "needs_more_info";
  note: string;
  priority: ReviewPriority;
  priority_override: ReviewPriority | null;
  override_reason: string | null;
  reviewer: string;
  created_at: string;
  evidence_snapshot: Investigation;
}

export interface InvoiceSearchResult {
  invoice_id: string;
  invoice_number: string;
  supplier_id: string;
  supplier_name: string;
  gross_amount: number;
  currency: string;
  status: string;
}
