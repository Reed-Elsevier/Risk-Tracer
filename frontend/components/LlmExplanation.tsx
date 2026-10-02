"use client";

import { useState } from "react";

import { fetchExplanation } from "@/lib/api";

export default function LlmExplanation({ invoiceId, available }: { invoiceId: string; available: boolean }) {
  const [narrative, setNarrative] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function explain() {
    setLoading(true);
    setError("");
    try {
      const result = await fetchExplanation(invoiceId);
      setNarrative(result.narrative);
      setSources(result.source_ids);
    } catch (explanationError) {
      setError(explanationError instanceof Error ? explanationError.message : "Could not generate explanation");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white/80 p-5 shadow-card">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">Optional assistant</p>
          <h2 className="text-xl font-semibold tracking-tight text-ink">Explain the cited evidence</h2>
          <p className="mt-1 max-w-2xl text-sm text-slate-500">The model can summarize the records. It does not set priority or conclude fraud.</p>
        </div>
        <button type="button" disabled={!available || loading} onClick={explain} className="rounded-lg border border-moss px-4 py-2 text-sm font-semibold text-moss hover:bg-mist disabled:cursor-not-allowed disabled:opacity-40">
          {!available ? "Key not configured" : loading ? "Explaining…" : "Explain"}
        </button>
      </div>
      {narrative && <div className="mt-5 rounded-xl bg-[#f2f6f0] p-4 text-sm leading-6 text-slate-700"><p>{narrative}</p>{sources.length > 0 && <p className="mt-3 font-mono text-xs text-moss">Cited: {sources.join(", ")}</p>}</div>}
      {error && <p className="mt-4 rounded-lg bg-[#fff0ea] px-3 py-2 text-sm text-ember">{error}</p>}
    </section>
  );
}
