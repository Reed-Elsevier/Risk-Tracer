export default function InvestigationNarrative({
  status,
  text,
  sourceIds
}: {
  status: "shown" | "unavailable";
  text: string;
  sourceIds: string[];
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white/80 p-5 shadow-card">
      <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">Investigation narrative</p>
      <h2 className="text-xl font-semibold tracking-tight text-ink">What to read first</h2>
      {status === "shown" ? (
        <div className="mt-4 rounded-xl bg-[#f2f6f0] p-4 text-sm leading-6 text-slate-700">
          <p>{text}</p>
          {sourceIds.length > 0 && <p className="mt-3 font-mono text-xs text-moss">Cited: {sourceIds.join(", ")}</p>}
        </div>
      ) : (
        <p className="mt-4 rounded-xl bg-[#f7f4ee] px-4 py-3 text-sm text-slate-600">The investigation narrative was not shown.</p>
      )}
    </section>
  );
}
