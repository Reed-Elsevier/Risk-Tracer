"use client";

import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useId, useState } from "react";

import { searchInvoices } from "@/lib/api";
import type { InvoiceSearchResult } from "@/lib/types";

export default function InvoiceSearch({ variant = "bar" }: { variant?: "bar" | "desk" }) {
  const router = useRouter();
  const listId = useId();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<InvoiceSearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const desk = variant === "desk";

  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      setStatus("idle");
      return;
    }
    setStatus("loading");
    const handle = window.setTimeout(() => {
      searchInvoices(trimmed)
        .then((next) => {
          setResults(next);
          setStatus("ready");
          setOpen(true);
        })
        .catch(() => {
          setResults([]);
          setStatus("error");
          setOpen(true);
        });
    }, 180);
    return () => window.clearTimeout(handle);
  }, [query]);

  function openInvoice(invoiceId: string) {
    setOpen(false);
    setQuery(invoiceId);
    router.push(`/investigations/${invoiceId}`);
  }

  const showPanel = desk ? status !== "idle" : open && (results.length > 0 || status === "error");

  return (
    <div className={desk ? "flex h-full min-h-[22rem] w-full flex-col rounded-2xl border border-[#c9d4cc] bg-white shadow-card" : "relative w-full max-w-md"}>
      <div className={desk
        ? "flex items-center gap-3 border-b border-[#e4ebe6] px-5 py-5"
        : "flex items-center gap-2 rounded-xl border border-[#c9d4cc] bg-white px-3 py-2 shadow-card"}>
        <Search size={desk ? 22 : 17} className="shrink-0 text-moss" aria-hidden="true" />
        <input
          aria-label="Find an invoice"
          aria-controls={listId}
          aria-expanded={showPanel}
          value={query}
          autoFocus={desk}
          onFocus={() => setOpen(true)}
          onChange={(event) => {
            setQuery(event.target.value);
            setOpen(true);
          }}
          onKeyDown={(event) => {
            if (event.key === "Enter" && results[0]) {
              event.preventDefault();
              openInvoice(results[0].invoice_id);
            }
            if (event.key === "Escape") setOpen(false);
          }}
          placeholder="Invoice id, number, or supplier"
          className={desk
            ? "w-full bg-transparent text-xl text-ink outline-none placeholder:text-[#3e524c]"
            : "w-full bg-transparent text-sm text-ink outline-none placeholder:text-[#3e524c]"}
        />
      </div>
      {desk && status === "idle" && (
        <p className="px-5 py-4 text-sm leading-6 text-[#3e524c]">Matches stay on this desk. Press Enter to open the first one.</p>
      )}
      {showPanel && (
        <div
          id={listId}
          className={desk
            ? "min-h-0 flex-1 overflow-auto"
            : "absolute z-20 mt-2 w-full overflow-hidden rounded-xl border border-[#c9d4cc] bg-white p-1 shadow-card"}
        >
          {status === "loading" && <p className="px-4 py-3 text-sm text-[#3e524c]">Searching…</p>}
          {status === "error" && (
            <p className="px-4 py-3 text-sm text-ink">Search is unavailable. Check that the API is running, then try again.</p>
          )}
          {status === "ready" && results.length === 0 && (
            <p className="px-4 py-3 text-sm text-ink">No invoice matches “{query.trim()}”.</p>
          )}
          {status === "ready" && results.length > 0 && (
            <ul className={desk ? "max-h-80 overflow-auto py-1" : ""}>
              {results.map((result) => (
                <li key={result.invoice_id}>
                  <button
                    type="button"
                    onClick={() => openInvoice(result.invoice_id)}
                    className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left text-sm hover:bg-mist"
                  >
                    <span>
                      <span className="block font-semibold text-ink">{result.invoice_id}</span>
                      <span className="mt-0.5 block text-xs text-[#3e524c]">{result.supplier_name}</span>
                    </span>
                    <span className="shrink-0 text-xs tabular-nums text-[#3e524c]">
                      {result.currency} {result.gross_amount.toLocaleString()}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
