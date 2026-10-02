"use client";

import Link from "next/link";
import { ArrowUpRight, FileWarning, ShieldAlert, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";

import { fetchDecisionHistory, fetchInvestigation } from "@/lib/api";
import type { Investigation, ReviewDecision } from "@/lib/types";
import AppShell from "@/components/AppShell";
import DecisionForm from "@/components/DecisionForm";
import DecisionHistory from "@/components/DecisionHistory";
import EvidenceBrief from "@/components/EvidenceBrief";
import InvestigationNarrative from "@/components/InvestigationNarrative";
import OwnershipGraph from "@/components/OwnershipGraph";
import PriorityBadge from "@/components/PriorityBadge";
import SignalCard from "@/components/SignalCard";

function amount(currency: string, value: number) {
  return `${currency} ${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function InvestigationView({ invoiceId }: { invoiceId: string }) {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [decisions, setDecisions] = useState<ReviewDecision[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    setInvestigation(null);
    setError("");
    Promise.all([fetchInvestigation(invoiceId), fetchDecisionHistory(invoiceId)])
      .then(([nextInvestigation, nextDecisions]) => {
        setInvestigation(nextInvestigation);
        setDecisions(nextDecisions);
      })
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Could not load investigation"));
  }, [invoiceId]);

  if (error) {
    return (
      <AppShell>
        <div className="mx-auto max-w-3xl px-6 py-10">
          <div className="rounded-2xl border border-[#f48529] bg-white p-6 text-black">
            <h1 className="text-xl font-semibold">Investigation unavailable</h1>
            <p className="mt-2 text-sm text-ink">{error}</p>
            <div className="mt-4 flex flex-wrap gap-4 text-sm font-semibold">
              <Link href="/" className="text-black underline decoration-[#1e4e8c] underline-offset-4">Back to Home</Link>
              <Link href="/investigations/INV0021439" className="text-black underline decoration-[#1e4e8c] underline-offset-4">Open the verified case</Link>
            </div>
          </div>
        </div>
      </AppShell>
    );
  }
  if (!investigation) {
    return (
      <AppShell>
        <div className="mx-auto max-w-7xl animate-pulse px-6 py-10">
          <div className="h-8 w-64 rounded bg-mist" />
          <div className="mt-8 h-56 rounded-2xl bg-white" />
        </div>
      </AppShell>
    );
  }

  const { invoice, supplier, priority, signals } = investigation;
  const nextDecisions = (decision: ReviewDecision) => setDecisions((current) => [decision, ...current]);

  return (
    <AppShell>
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-black">Investigation</p>
            <div className="mt-2 flex flex-wrap items-center gap-3"><h1 className="text-3xl font-bold tracking-tight text-ink">{invoice.invoice_id}</h1><PriorityBadge value={priority.value} /></div>
            <p className="mt-2 text-base text-black/70"><Link href={`/suppliers/${supplier.supplier_id}`} className="font-semibold text-black underline decoration-[#1e4e8c] underline-offset-4 hover:underline">{supplier.supplier_name}</Link> · {supplier.supplier_id} · {supplier.country}</p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-right sm:grid-cols-4">
            <div><p className="text-[10px] font-bold uppercase tracking-widest text-black/50">Gross amount</p><p className="mt-1 font-semibold text-ink">{amount(invoice.currency, invoice.gross_amount)}</p></div>
            <div><p className="text-[10px] font-bold uppercase tracking-widest text-black/50">Status</p><p className="mt-1 font-semibold text-ink">{invoice.status}</p></div>
            <div><p className="text-[10px] font-bold uppercase tracking-widest text-black/50">Invoice no.</p><p className="mt-1 font-mono text-xs font-semibold text-ink">{invoice.invoice_number}</p></div>
            <div><p className="text-[10px] font-bold uppercase tracking-widest text-black/50">Priority rule</p><p className="mt-1 max-w-[170px] text-xs leading-4 text-black/70">{priority.rule}</p></div>
          </div>
        </div>

        <div className="mt-8">
          <InvestigationNarrative status={investigation.narrative.status} text={investigation.narrative.text} sourceIds={investigation.narrative.source_ids} />
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
          <EvidenceBrief sentences={investigation.evidence_brief.sentences} suggestedNextStep={investigation.evidence_brief.suggested_next_step} retrospective={investigation.evidence_brief.retrospective} />
          <SignalCard eyebrow="Invoice exceptions" title={`${signals.exceptions.length} recorded context item${signals.exceptions.length === 1 ? "" : "s"}`} tone={signals.exceptions.length ? "watch" : "clear"}>
            {signals.exceptions.length === 0 ? <p className="text-sm text-black/70">No invoice exceptions are recorded.</p> : <div className="space-y-3">{signals.exceptions.map((exception) => <div key={exception.exception_id} className="flex gap-3 rounded-xl border border-[#e6b325] bg-[#fbf4dc] p-3"><FileWarning size={18} className="mt-0.5 shrink-0 text-[#7a5b00]" /><div><p className="text-sm font-semibold text-ink">{exception.exception_type}</p><p className="mt-1 text-xs text-black/60"><span className="font-mono">{exception.exception_id}</span> · {exception.resolved_at ? "Resolved" : "Unresolved"}</p>{exception.resolution && <p className="mt-2 text-xs text-black/70">{exception.resolution}</p>}</div></div>)}</div>}
          </SignalCard>
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-3">
          <SignalCard eyebrow="Possible duplicate submission" title={`${signals.duplicate.matches.length} comparison record${signals.duplicate.matches.length === 1 ? "" : "s"}`} tone={signals.duplicate.matches.length ? "alert" : "clear"}>
            {signals.duplicate.matches.length === 0 ? <p className="text-sm text-black/70">No same-supplier, same-currency comparison record met the rule.</p> : <div className="space-y-3">
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl border border-black/15 bg-white p-3">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-black">Subject invoice</p>
                  <p className="mt-2 font-mono text-sm font-semibold text-ink">{invoice.invoice_id}</p>
                  <p className="mt-2 text-xs text-black/70">{invoice.invoice_number} · {amount(invoice.currency, invoice.gross_amount)}</p>
                  <p className="mt-2 text-xs text-black/60">Status: {invoice.status}</p>
                </div>
                {signals.duplicate.matches.slice(0, 3).map((match) => <div key={match.invoice_id} className="rounded-xl bg-white p-3"><div className="flex items-center justify-between gap-2"><span className="font-mono text-sm font-semibold text-ink">{match.invoice_id}</span><span className="text-xs font-semibold text-black">{match.score.toFixed(0)} score</span></div><p className="mt-2 text-xs text-black/70">{match.invoice_number} · {amount(match.currency, match.gross_amount || 0)}</p><p className="mt-2 text-xs text-black/60">Status: {match.status}{match.payment && <> · <span className="font-mono">{match.payment.payment_id}</span> recorded</>}</p></div>)}
              </div>
            </div>}
          </SignalCard>
          <SignalCard eyebrow="PO integrity" title={signals.po_integrity.reasons.length ? "Review required" : "No signal"} tone={signals.po_integrity.reasons.length ? "watch" : "clear"}>
            {signals.po_integrity.reasons.length ? <ul className="space-y-2 text-sm text-black/80">{signals.po_integrity.reasons.map((reason) => <li key={reason.code} className="flex gap-2"><TriangleAlert size={16} className="mt-0.5 shrink-0 text-[#7a5b00]" />{reason.label}</li>)}</ul> : <p className="text-sm text-black/70">{signals.po_integrity.purchase_order ? `PO ${signals.po_integrity.purchase_order.po_id} matches supplier and currency.` : "No purchase order record was available."}</p>}
            {invoice.po_id && <p className="mt-4 font-mono text-xs text-black/50">{invoice.po_id}</p>}
          </SignalCard>
          <SignalCard eyebrow="Watchlist exposure" title={signals.watchlist.direct_match ? "Direct entity match" : `${signals.watchlist.exposures.length} indirect path${signals.watchlist.exposures.length === 1 ? "" : "s"}`} tone={signals.watchlist.direct_match || signals.watchlist.exposures.length ? "record" : "clear"}>
            {signals.watchlist.direct_match && <div className="rounded-xl border border-[#1e4e8c] bg-[#eef3fa] p-3 text-sm text-black"><div className="flex gap-2"><ShieldAlert size={18} className="shrink-0 text-[#1e4e8c]" /><span>{signals.watchlist.direct_match.list_type} · {signals.watchlist.direct_match.reason}</span></div><p className="mt-2 font-mono text-xs text-[#1e4e8c]">{signals.watchlist.direct_match.watchlist_entry_id} · listed {signals.watchlist.direct_match.listed_date.slice(0, 10)}</p></div>}
            {signals.watchlist.exposures.length > 0 && <div className="space-y-3">{signals.watchlist.exposures.map((exposure) => <div key={exposure.watchlist.watchlist_entry_id} className="rounded-xl border border-[#1e4e8c] bg-white p-3"><p className="text-sm leading-5 text-black">{exposure.hop_count}-hop path to {exposure.watchlist.entity_id}</p><div className="mt-2 flex flex-wrap gap-1.5">{exposure.links.map((link) => <span key={link.ownership_link_id} className="rounded-md bg-[#eef3fa] px-2 py-1 font-mono text-[10px] text-[#1e4e8c]">{link.ownership_link_id} · {link.ownership_pct}% · {link.effective_date.slice(0, 10)}</span>)}<span className="rounded-md bg-[#1e4e8c] px-2 py-1 font-mono text-[10px] text-white">{exposure.watchlist.watchlist_entry_id} · listed {exposure.watchlist.listed_date.slice(0, 10)}</span></div></div>)}</div>}
            {!signals.watchlist.direct_match && signals.watchlist.exposures.length === 0 && <p className="text-sm text-black/70">No exact entity watchlist match or bounded upstream exposure was found.</p>}
          </SignalCard>
        </div>

        <div className="mt-5"><OwnershipGraph graph={investigation.graph} /></div>

        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <DecisionForm invoiceId={invoice.invoice_id} currentPriority={priority.value} initialNote={investigation.narrative.status === "shown" ? investigation.narrative.checklist : ""} narrative={investigation.narrative} onSaved={nextDecisions} />
          <DecisionHistory decisions={decisions} />
        </div>

        <footer className="flex flex-wrap items-center justify-between gap-3 py-8 text-xs text-black/70"><span>RiskTracer keeps the initial priority deterministic and reviewable.</span><a href="https://github.com" className="inline-flex items-center gap-1 underline decoration-[#1e4e8c] underline-offset-4">Source records only <ArrowUpRight size={13} /></a></footer>
      </div>
    </AppShell>
  );
}
