import type { ReviewDecision } from "@/lib/types";

export default function DecisionHistory({ decisions }: { decisions: ReviewDecision[] }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white/80 p-5 shadow-card">
      <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">Review history</p>
      <h2 className="text-xl font-semibold tracking-tight text-ink">Recorded decisions</h2>
      {decisions.length === 0 ? (
        <p className="mt-4 text-sm text-slate-500">No decision has been recorded for this investigation.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {decisions.map((decision) => (
            <div key={decision.decision_id} className="rounded-xl border border-slate-100 bg-[#fbfcf8] p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-semibold capitalize text-ink">{decision.disposition.replaceAll("_", " ")}</span>
                <span className="text-xs text-slate-500">{new Date(decision.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-1 text-xs text-moss">{decision.priority} · {decision.reviewer}</p>
              {decision.note && <p className="mt-3 text-sm leading-6 text-slate-700">{decision.note}</p>}
              {decision.override_reason && <p className="mt-2 text-xs text-slate-500">Override: {decision.override_reason}</p>}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
