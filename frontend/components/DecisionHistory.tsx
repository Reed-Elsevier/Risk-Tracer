import type { ReviewDecision } from "@/lib/types";

export default function DecisionHistory({ decisions }: { decisions: ReviewDecision[] }) {
  return (
    <section className="rounded-2xl border border-black/15 bg-white p-5 shadow-card">
      <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-black/60">Review history</p>
      <h2 className="text-xl font-semibold tracking-tight text-ink">Recorded decisions</h2>
      {decisions.length === 0 ? (
        <p className="mt-4 text-sm text-black/60">No decision has been recorded for this investigation.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {decisions.map((decision) => (
            <div key={decision.decision_id} className="rounded-xl border border-black/10 bg-white p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-semibold capitalize text-ink">{decision.disposition.replaceAll("_", " ")}</span>
                <span className="text-xs text-black/60">{new Date(decision.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-1 text-xs text-black">{decision.priority} · {decision.reviewer}</p>
              {decision.note && <p className="mt-3 text-sm leading-6 text-black/80">{decision.note}</p>}
              {decision.override_reason && <p className="mt-2 text-xs text-black/60">Override: {decision.override_reason}</p>}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
