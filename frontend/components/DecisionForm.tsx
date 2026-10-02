"use client";

import { useState } from "react";

import { saveDecision } from "@/lib/api";
import type { ReviewDecision, ReviewPriority } from "@/lib/types";

export default function DecisionForm({
  invoiceId,
  currentPriority,
  onSaved
}: {
  invoiceId: string;
  currentPriority: ReviewPriority;
  onSaved: (decision: ReviewDecision) => void;
}) {
  const [disposition, setDisposition] = useState<ReviewDecision["disposition"]>("needs_more_info");
  const [note, setNote] = useState("");
  const [reviewer, setReviewer] = useState("");
  const [override, setOverride] = useState<ReviewPriority | "">("");
  const [overrideReason, setOverrideReason] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit() {
    setSaving(true);
    setError("");
    try {
      const decision = await saveDecision(invoiceId, {
        disposition,
        note,
        reviewer,
        ...(override ? { priority_override: override, override_reason: overrideReason } : {})
      });
      onSaved(decision);
      setNote("");
      setOverride("");
      setOverrideReason("");
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Could not save decision");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white/80 p-5 shadow-card">
      <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">Human review</p>
      <h2 className="text-xl font-semibold tracking-tight text-ink">Record a review decision</h2>
      <p className="mt-1 text-sm text-slate-500">The evidence snapshot is stored with the decision.</p>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="text-sm font-semibold text-ink">Disposition
          <select value={disposition} onChange={(event) => setDisposition(event.target.value as ReviewDecision["disposition"])} className="mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 font-normal outline-none focus:border-moss">
            <option value="needs_more_info">Needs more information</option>
            <option value="escalate">Escalate</option>
            <option value="clear">Clear</option>
          </select>
        </label>
        <label className="text-sm font-semibold text-ink">Reviewer
          <input value={reviewer} onChange={(event) => setReviewer(event.target.value)} placeholder="Name or email" className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal outline-none focus:border-moss" />
        </label>
        <label className="text-sm font-semibold text-ink sm:col-span-2">Note
          <textarea value={note} onChange={(event) => setNote(event.target.value)} rows={3} placeholder="What did you verify or request?" className="mt-2 w-full resize-y rounded-lg border border-slate-200 px-3 py-2 font-normal outline-none focus:border-moss" />
        </label>
        <label className="text-sm font-semibold text-ink">Priority override <span className="font-normal text-slate-400">(optional)</span>
          <select value={override} onChange={(event) => setOverride(event.target.value as ReviewPriority | "")} className="mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 font-normal outline-none focus:border-moss">
            <option value="">Keep {currentPriority}</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="No flagged signals">No flagged signals</option>
          </select>
        </label>
        {override && <label className="text-sm font-semibold text-ink">Override reason
          <input value={overrideReason} onChange={(event) => setOverrideReason(event.target.value)} placeholder="Why should the initial rule be overridden?" className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal outline-none focus:border-moss" />
        </label>}
      </div>
      {error && <p className="mt-4 rounded-lg bg-[#fff0ea] px-3 py-2 text-sm text-ember">{error}</p>}
      <button type="button" disabled={saving || !reviewer.trim() || (override !== "" && !overrideReason.trim())} onClick={submit} className="mt-5 rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-white transition hover:bg-moss disabled:cursor-not-allowed disabled:opacity-40">
        {saving ? "Saving…" : "Save review decision"}
      </button>
    </section>
  );
}
