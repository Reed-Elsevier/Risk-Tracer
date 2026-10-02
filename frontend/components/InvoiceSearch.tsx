"use client";

import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { searchInvoices } from "@/lib/api";
import type { InvoiceSearchResult } from "@/lib/types";

export default function InvoiceSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<InvoiceSearchResult[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      searchInvoices(query)
        .then(setResults)
        .catch(() => setResults([]));
    }, 180);
    return () => window.clearTimeout(handle);
  }, [query]);

  return (
    <div className="relative w-full max-w-md">
      <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
        <Search size={17} className="text-slate-400" />
        <input
          aria-label="Find an invoice"
          value={query}
          onFocus={() => setOpen(true)}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Find invoice, number, or supplier…"
          className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
        />
      </div>
      {open && results.length > 0 && (
        <div className="absolute z-20 mt-2 w-full overflow-hidden rounded-xl border border-slate-200 bg-white p-1 shadow-xl">
          {results.map((result) => (
            <button
              type="button"
              key={result.invoice_id}
              onClick={() => {
                setOpen(false);
                setQuery(result.invoice_id);
                router.push(`/investigations/${result.invoice_id}`);
              }}
              className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm hover:bg-mist"
            >
              <span>
                <span className="block font-semibold text-ink">{result.invoice_id}</span>
                <span className="block text-xs text-slate-500">{result.supplier_name}</span>
              </span>
              <span className="text-xs text-slate-500">{result.currency} {result.gross_amount.toLocaleString()}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
