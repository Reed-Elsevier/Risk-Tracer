"use client";

import Link from "next/link";
import { ArrowUpRight, FileWarning, ShieldAlert, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";

import { fetchDecisionHistory, fetchInvestigation } from "@/lib/api";
import type { Investigation, ReviewDecision } from "@/lib/types";
import DecisionForm from "@/components/DecisionForm";
import DecisionHistory from "@/components/DecisionHistory";
import EvidenceBrief from "@/components/EvidenceBrief";
import InvoiceSearch from "@/components/InvoiceSearch";
import LlmExplanation from "@/components/LlmExplanation";
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
    return <main className="min-h-screen bg-paper px-6 py-10"><div className="mx-auto max-w-3xl rounded-2xl border border-[#efc7b9] bg-[#fff4ef] p-6 text-ember"><h1 className="text-xl font-semibold">Investigation unavailable</h1><p className="mt-2 text-sm">{error}</p><Link href="/investigations/INV0021439" className="mt-4 inline-flex text-sm font-semibold underline">Open the demo investigation</Link></div></main>;
  }
  if (!investigation) {
    return <main className="min-h-screen bg-paper px-6 py-10"><div className="mx-auto max-w-7xl animate-pulse"><div className="h-8 w-64 rounded bg-mist" /><div className="mt-8 h-56 rounded-2xl bg-white" /></div></main>;
  }

  const { invoice, supplier, priority, signals } = investigation;
  const nextDecisions = (decision: ReviewDecision) => setDecisions((current) => [decision, ...current]);

  return (
    <main className="min-h-screen bg-paper">
      <header className="border-b border-slate-200 bg-paper/90 px-6 py-5 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-ink text-sm font-black text-[#b8dfc5]">R</span><span><span className="block text-sm font-black tracking-tight text-ink">RiskTracer</span><span className="block text-[10px] uppercase tracking-[0.18em] text-slate-500">Evidence-led review</span></span></Link>
          <InvoiceSearch />
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-moss">Investigation</p>
            <div className="mt-2 flex flex-wrap items-center gap-3"><h1 className="text-3xl font-black tracking-tight text-ink">{invoice.invoice_id}</h1><PriorityBadge value={priority.value} /></div>
            <p className="mt-2 text-base text-slate-600"><Link href={`/suppliers/${supplier.supplier_id}`} className="font-semibold text-moss underline-offset-4 hover:underline">{supplier.supplier_name}</Link> · {supplier.supplier_id} · {supplier.country}</p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-right sm:grid-cols-4">
            <div><p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Gross amount</p><p className="mt-1 font-semibold text-ink">{amount(invoice.currency, invoice.gross_amount)}</p></div>
            <div><p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Status</p><p className="mt-1 font-semibold text-ink">{invoice.status}</p></div>
            <div><p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Invoice no.</p><p className="mt-1 font-mono text-xs font-semibold text-ink">{invoice.invoice_number}</p></div>
            <div><p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Priority rule</p><p className="mt-1 max-w-[170px] text-xs leading-4 text-slate-600">{priority.rule}</p></div>
          </div>
        </div>

        <div className="mt-8 grid gap-5 lg:grid-cols-3">
          <SignalCard eyebrow="Possible duplicate submission" title={`${signals.duplicate.matches.length} comparison record${signals.duplicate.matches.length === 1 ? "" : "s"}`} tone={signals.duplicate.matches.length ? "alert" : "clear"}>
            {signals.duplicate.matches.length === 0 ? <p className="text-sm text-slate-600">No same-supplier, same-currency comparison record met the rule.</p> : <div className="space-y-3">{signals.duplicate.matches.slice(0, 3).map((match) => <div key={match.invoice_id} className="rounded-xl bg-white p-3"><div className="flex items-center justify-between gap-2"><span className="font-mono text-sm font-semibold text-ink">{match.invoice_id}</span><span className="text-xs font-semibold text-ember">{match.score.toFixed(0)} score</span></div><p className="mt-2 text-xs text-slate-600">{match.invoice_number} · {amount(match.currency, match.gross_amount || 0)}</p><p className="mt-2 text-xs text-slate-500">Status: {match.status}{match.payment && <> · <span className="font-mono">{match.payment.payment_id}</span> recorded</>}</p></div>)}</div>}
          </SignalCard>
          <SignalCard eyebrow="PO integrity" title={signals.po_integrity.reasons.length ? "Review required" : "No signal"} tone={signals.po_integrity.reasons.length ? "watch" : "clear"}>
            {signals.po_integrity.reasons.length ? <ul className="space-y-2 text-sm text-slate-700">{signals.po_integrity.reasons.map((reason) => <li key={reason.code} className="flex gap-2"><TriangleAlert size={16} className="mt-0.5 shrink-0 text-gold" />{reason.label}</li>)}</ul> : <p className="text-sm text-slate-600">{signals.po_integrity.purchase_order ? `PO ${signals.po_integrity.purchase_order.po_id} matches supplier and currency.` : "No purchase order record was available."}</p>}
            {invoice.po_id && <p className="mt-4 font-mono text-xs text-slate-400">{invoice.po_id}</p>}
          </SignalCard>
          <SignalCard eyebrow="Watchlist exposure" title={signals.watchlist.direct_match ? "Direct entity match" : `${signals.watchlist.exposures.length} indirect path${signals.watchlist.exposures.length === 1 ? "" : "s"}`} tone={signals.watchlist.direct_match || signals.watchlist.exposures.length ? "alert" : "clear"}>
            {signals.watchlist.direct_match && <div className="rounded-xl bg-[#fff0ea] p-3 text-sm text-slate-700"><div className="flex gap-2"><ShieldAlert size={18} className="shrink-0 text-ember" /><span>{signals.watchlist.direct_match.list_type} · {signals.watchlist.direct_match.reason}</span></div><p className="mt-2 font-mono text-xs text-ember">{signals.watchlist.direct_match.watchlist_entry_id}</p></div>}
            {signals.watchlist.exposures.length > 0 && <div className="space-y-3">{signals.watchlist.exposures.map((exposure) => <div key={exposure.watchlist.watchlist_entry_id} className="rounded-xl bg-[#fffaf0] p-3"><p className="text-sm leading-5 text-slate-700">{exposure.hop_count}-hop path to {exposure.watchlist.entity_id}</p><div className="mt-2 flex flex-wrap gap-1.5">{exposure.links.map((link) => <span key={link.ownership_link_id} className="rounded-md bg-white px-2 py-1 font-mono text-[10px] text-gold">{link.ownership_link_id} · {link.ownership_pct}%</span>)}<span className="rounded-md bg-white px-2 py-1 font-mono text-[10px] text-ember">{exposure.watchlist.watchlist_entry_id}</span></div></div>)}</div>}
            {!signals.watchlist.direct_match && signals.watchlist.exposures.length === 0 && <p className="text-sm text-slate-600">No exact entity watchlist match or bounded upstream exposure was found.</p>}
          </SignalCard>
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
          <EvidenceBrief sentences={investigation.evidence_brief.sentences} suggestedNextStep={investigation.evidence_brief.suggested_next_step} retrospective={investigation.evidence_brief.retrospective} />
          <SignalCard eyebrow="Invoice exceptions" title={`${signals.exceptions.length} recorded context item${signals.exceptions.length === 1 ? "" : "s"}`} tone={signals.exceptions.length ? "watch" : "clear"}>
            {signals.exceptions.length === 0 ? <p className="text-sm text-slate-600">No invoice exceptions are recorded.</p> : <div className="space-y-3">{signals.exceptions.map((exception) => <div key={exception.exception_id} className="flex gap-3 rounded-xl bg-[#fffcf4] p-3"><FileWarning size={18} className="mt-0.5 shrink-0 text-gold" /><div><p className="text-sm font-semibold text-ink">{exception.exception_type}</p><p className="mt-1 text-xs text-slate-500"><span className="font-mono">{exception.exception_id}</span> · {exception.resolved_at ? "Resolved" : "Unresolved"}</p>{exception.resolution && <p className="mt-2 text-xs text-slate-600">{exception.resolution}</p>}</div></div>)}</div>}
          </SignalCard>
        </div>

        <div className="mt-5"><OwnershipGraph graph={investigation.graph} /></div>

        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <DecisionForm invoiceId={invoice.invoice_id} currentPriority={priority.value} onSaved={nextDecisions} />
          <DecisionHistory decisions={decisions} />
        </div>

        <div className="mt-5"><LlmExplanation invoiceId={invoice.invoice_id} available={investigation.llm_available} /></div>

        <footer className="flex flex-wrap items-center justify-between gap-3 py-8 text-xs text-slate-400"><span>RiskTracer keeps the initial priority deterministic and reviewable.</span><a href="https://github.com" className="inline-flex items-center gap-1 hover:text-moss">Source records only <ArrowUpRight size={13} /></a></footer>
      </div>
    </main>
  );
}
