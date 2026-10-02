"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchSupplierProfile } from "@/lib/api";
import type { SupplierProfile } from "@/lib/types";
import InvoiceSearch from "@/components/InvoiceSearch";

export default function SupplierView({ supplierId }: { supplierId: string }) {
  const [profile, setProfile] = useState<SupplierProfile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchSupplierProfile(supplierId).then(setProfile).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Could not load supplier"));
  }, [supplierId]);

  if (error) return <main className="min-h-screen bg-paper px-6 py-10"><div className="mx-auto max-w-3xl rounded-2xl bg-[#fff4ef] p-6 text-ember">{error}</div></main>;
  if (!profile) return <main className="min-h-screen bg-paper px-6 py-10"><div className="mx-auto max-w-5xl animate-pulse"><div className="h-8 w-72 rounded bg-mist" /><div className="mt-8 h-64 rounded-2xl bg-white" /></div></main>;

  const { supplier, invoices } = profile;
  return (
    <main className="min-h-screen bg-paper">
      <header className="border-b border-slate-200 px-6 py-5"><div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4"><Link href="/" className="text-sm font-black tracking-tight text-ink">RiskTracer</Link><InvoiceSearch /></div></header>
      <div className="mx-auto max-w-5xl px-6 py-10">
        <Link href="/investigations/INV0021439" className="text-sm font-semibold text-moss hover:underline">← Back to demo investigation</Link>
        <div className="mt-6 rounded-2xl border border-slate-200 bg-white/80 p-6 shadow-card">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-moss">Supplier profile</p>
          <h1 className="mt-2 text-3xl font-black tracking-tight text-ink">{supplier.supplier_name}</h1>
          <p className="mt-2 text-sm text-slate-500">{supplier.supplier_id} · {supplier.entity_id} · {supplier.country} · {supplier.category}</p>
          <div className="mt-6 grid gap-4 sm:grid-cols-4"><div><p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Risk tier</p><p className="mt-1 font-semibold text-ink">{supplier.risk_tier}</p></div><div><p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Status</p><p className="mt-1 font-semibold text-ink">{supplier.status}</p></div><div><p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Payment terms</p><p className="mt-1 font-semibold text-ink">{supplier.payment_terms_days} days</p></div><div><p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Invoices</p><p className="mt-1 font-semibold text-ink">{invoices.length.toLocaleString()}</p></div></div>
        </div>
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white/80 p-6 shadow-card"><p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Invoice records</p><div className="mt-4 overflow-x-auto"><table className="w-full min-w-[680px] text-left text-sm"><thead className="border-b border-slate-200 text-[10px] uppercase tracking-widest text-slate-400"><tr><th className="pb-3">Invoice</th><th className="pb-3">Number</th><th className="pb-3">Amount</th><th className="pb-3">Status</th><th className="pb-3">Date</th></tr></thead><tbody>{invoices.map((invoice) => <tr key={invoice.invoice_id} className="border-b border-slate-100 last:border-0"><td className="py-3"><Link href={`/investigations/${invoice.invoice_id}`} className="font-mono font-semibold text-moss hover:underline">{invoice.invoice_id}</Link></td><td className="py-3 font-mono text-xs text-slate-600">{invoice.invoice_number}</td><td className="py-3 text-slate-700">{invoice.currency} {invoice.gross_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td><td className="py-3 text-slate-700">{invoice.status}</td><td className="py-3 text-slate-500">{invoice.invoice_date.slice(0, 10)}</td></tr>)}</tbody></table></div></section>
      </div>
    </main>
  );
}
