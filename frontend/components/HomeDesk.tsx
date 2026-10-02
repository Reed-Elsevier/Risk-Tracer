"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import AppShell from "@/components/AppShell";
import InvoiceSearch from "@/components/InvoiceSearch";
import PriorityBadge from "@/components/PriorityBadge";
import { fetchInvestigation } from "@/lib/api";
import type { Investigation } from "@/lib/types";

const DEMO_INVOICE_ID = "INV0021439";

function amount(currency: string, value: number) {
  return `${currency} ${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function HomeDesk() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchInvestigation(DEMO_INVOICE_ID)
      .then(setInvestigation)
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Could not load the verified case"));
  }, []);

  const invoice = investigation?.invoice;
  const supplier = investigation?.supplier;

  return (
    <AppShell search={false}>
      <div className="mx-auto max-w-7xl px-6 pb-16 pt-10">
        <h1 id="find-invoice" className="max-w-[18ch] text-4xl font-bold tracking-tight text-ink sm:text-5xl">
          Find an invoice
        </h1>
        <p className="mt-4 max-w-[62ch] text-base leading-7 text-black/70">
          Type an invoice id, number, or supplier, or open the verified case. A review shows signals from source records, the ownership path, and your decision.
        </p>

        <div className="mt-10 grid items-stretch gap-8 lg:grid-cols-[1.45fr_0.8fr] lg:gap-10">
          <InvoiceSearch variant="desk" />
          <article className="case-file relative flex h-full flex-col rounded-2xl border border-black/15 bg-white px-6 pb-6 pt-7 shadow-card">
            <svg viewBox="0 0 32 48" aria-hidden="true" className="absolute -top-4 right-8 h-10 w-7 text-moss">
              <path
                d="M10 16c0-6 12-6 12 2v18c0 6-12 6-12 0V14"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
              />
            </svg>
            <h2 className="text-2xl font-bold tracking-tight text-ink">{DEMO_INVOICE_ID}</h2>
            <p className="mt-2 text-sm leading-6 text-black/70">Verified case</p>
            {!investigation && !error && <p className="mt-6 text-sm text-black/70">Loading the case…</p>}
            {error && (
              <p className="mt-6 text-sm leading-6 text-ink">
                The case details did not load. {error}. You can still open the investigation.
              </p>
            )}
            {invoice && supplier && (
              <div className="mt-5 space-y-3">
                <p className="text-lg font-semibold leading-6 text-ink">{supplier.supplier_name}</p>
                <p className="text-sm text-black/70">{supplier.country} · {invoice.status}</p>
                <p className="text-sm font-semibold tabular-nums text-ink">{amount(invoice.currency, invoice.gross_amount)}</p>
                <PriorityBadge value={investigation.priority.value} />
                <p className="text-sm leading-6 text-black/70">{investigation.priority.rule}</p>
              </div>
            )}
            <Link
              href={`/investigations/${DEMO_INVOICE_ID}`}
              className="mt-auto inline-flex w-fit rounded-full bg-[#f48529] px-4 py-2.5 text-sm font-semibold text-black hover:bg-black hover:text-white"
            >
              Open investigation
            </Link>
          </article>
        </div>

        <section className="mt-20 border-t border-black/15 pt-10">
          <h2 className="text-2xl font-bold tracking-tight text-ink">How a review works</h2>
          <ol className="mt-8 grid gap-4 md:grid-cols-3">
            <li className="rounded-2xl border-t-4 border-[#f48529] bg-[#fff3e8] px-5 py-5">
              <p className="text-lg font-semibold text-[#9a4a12]">Signals</p>
              <p className="mt-2 text-sm leading-6 text-black">
                Possible duplicate submission, purchase-order integrity, watchlist exposure, and invoice exceptions. Each one names the source records it came from.
              </p>
            </li>
            <li className="rounded-2xl border-t-4 border-[#1e4e8c] bg-[#eef3fa] px-5 py-5">
              <p className="text-lg font-semibold text-[#1e4e8c]">Ownership path</p>
              <p className="mt-2 text-sm leading-6 text-black">
                Follow the recorded links from the supplier’s entity. Indirect watchlist exposure is a relationship signal, not proof of control.
              </p>
            </li>
            <li className="rounded-2xl border-t-4 border-[#146b43] bg-[#e8f5ee] px-5 py-5">
              <p className="text-lg font-semibold text-[#146b43]">Review decision</p>
              <p className="mt-2 text-sm leading-6 text-black">
                You escalate or clear, with a note. Review priority is a workflow label from evidence rules, not a fraud score. The narrative only explains.
              </p>
            </li>
          </ol>
        </section>
      </div>
    </AppShell>
  );
}
