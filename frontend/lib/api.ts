import type {
  Investigation,
  InvestigationNarrative,
  InvoiceSearchResult,
  ReviewDecision,
  SupplierProfile
} from "@/lib/types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers || {}) },
    cache: "no-store"
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchInvestigation(invoiceId: string): Promise<Investigation> {
  return apiFetch<Investigation>("/investigate", {
    method: "POST",
    body: JSON.stringify({ invoice_id: invoiceId })
  });
}

export function searchInvoices(query: string): Promise<InvoiceSearchResult[]> {
  return apiFetch<InvoiceSearchResult[]>(`/invoices?q=${encodeURIComponent(query)}&limit=8`);
}

export function fetchSupplierProfile(supplierId: string): Promise<SupplierProfile> {
  return apiFetch<SupplierProfile>(`/suppliers/${encodeURIComponent(supplierId)}`);
}

export function fetchDecisionHistory(invoiceId: string): Promise<ReviewDecision[]> {
  return apiFetch<ReviewDecision[]>(`/investigations/${encodeURIComponent(invoiceId)}/decisions`);
}

export function saveDecision(
  invoiceId: string,
  body: {
    disposition: ReviewDecision["disposition"];
    note: string;
    priority_override?: ReviewDecision["priority_override"];
    override_reason?: string;
    reviewer: string;
    narrative?: InvestigationNarrative;
  }
): Promise<ReviewDecision> {
  return apiFetch<ReviewDecision>(`/investigations/${encodeURIComponent(invoiceId)}/decisions`, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

