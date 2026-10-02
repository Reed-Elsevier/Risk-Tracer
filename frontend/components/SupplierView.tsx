"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import AppShell from "@/components/AppShell";
import { fetchSupplierProfile } from "@/lib/api";
import type { SupplierProfile } from "@/lib/types";

export default function SupplierView({ supplierId }: { supplierId: string }) {
  const [profile, setProfile] = useState<SupplierProfile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchSupplierProfile(supplierId).then(setProfile).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Could not load supplier"));
  }, [supplierId]);

  if (error) {
    return (
      <AppShell>
        <div className="mx-auto max-w-3xl px-6 py-10">
          <div className="rounded-2xl border border-[#f48529] bg-white p-6 text-ink">
            <h1 className="text-xl font-semibold text-black">Supplier unavailable</h1>
            <p className="mt-2 text-sm">{error}</p>
            <Link href="/" className="mt-4 inline-flex text-sm font-semibold text-black underline decoration-[#1e4e8c] underline-offset-4">Back to Home</Link>
          </div>
        </div>
      </AppShell>
    );
  }
  if (!profile) {
    return (
      <AppShell>
        <div className="mx-auto max-w-5xl animate-pulse px-6 py-10">
          <div className="h-8 w-72 rounded bg-mist" />
          <div className="mt-8 h-64 rounded-2xl bg-white" />
        </div>
      </AppShell>
    );
  }

  const { supplier, invoices } = profile;
  return (
    <AppShell>
      <div className="mx-auto max-w-5xl px-6 py-10">
        <div className="rounded-2xl border border-black/15 bg-white p-6 shadow-card">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-black">Supplier profile</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink">{supplier.supplier_name}</h1>
          <p className="mt-2 text-sm text-black/60">{supplier.supplier_id} · {supplier.entity_id} · {supplier.country} · {supplier.category}</p>
          <div className="mt-6 grid gap-4 sm:grid-cols-4"><div><p className="text-[10px] font-bold uppercase tracking-widest text-black/50">Risk tier</p><p className="mt-1 font-semibold text-ink">{supplier.risk_tier}</p></div><div><p className="text-[10px] font-bold uppercase tracking-widest text-black/50">Status</p><p className="mt-1 font-semibold text-ink">{supplier.status}</p></div><div><p className="text-[10px] font-bold uppercase tracking-widest text-black/50">Payment terms</p><p className="mt-1 font-semibold text-ink">{supplier.payment_terms_days} days</p></div><div><p className="text-[10px] font-bold uppercase tracking-widest text-black/50">Invoices</p><p className="mt-1 font-semibold text-ink">{invoices.length.toLocaleString()}</p></div></div>
        </div>
        <section className="mt-6 rounded-2xl border border-black/15 bg-white p-6 shadow-card"><p className="text-xs font-bold uppercase tracking-[0.18em] text-black/60">Invoice records</p><div className="mt-4 overflow-x-auto"><table className="w-full min-w-[680px] text-left text-sm"><thead className="border-b border-black/15 text-[10px] uppercase tracking-widest text-black/50"><tr><th className="pb-3">Invoice</th><th className="pb-3">Number</th><th className="pb-3">Amount</th><th className="pb-3">Status</th><th className="pb-3">Date</th></tr></thead><tbody>{invoices.map((invoice) => <tr key={invoice.invoice_id} className="border-b border-black/10 last:border-0"><td className="py-3"><Link href={`/investigations/${invoice.invoice_id}`} className="font-mono font-semibold text-black underline decoration-[#1e4e8c] underline-offset-4 hover:decoration-black">{invoice.invoice_id}</Link></td><td className="py-3 font-mono text-xs text-black/70">{invoice.invoice_number}</td><td className="py-3 text-black/80">{invoice.currency} {invoice.gross_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td><td className="py-3 text-black/80">{invoice.status}</td><td className="py-3 text-black/60">{invoice.invoice_date.slice(0, 10)}</td></tr>)}</tbody></table></div></section>
      </div>
    </AppShell>
  );
}
