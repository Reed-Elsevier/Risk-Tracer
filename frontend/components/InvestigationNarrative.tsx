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
    <section className="rounded-2xl border border-black/15 bg-white p-5 shadow-card">
      <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-black/60">Investigation narrative</p>
      <h2 className="text-xl font-semibold tracking-tight text-ink">What to read first</h2>
      {status === "shown" ? (
        <div className="mt-4 rounded-xl border border-black/15 bg-white p-4 text-sm leading-6 text-black/80">
          <p>{text}</p>
          {sourceIds.length > 0 && <p className="mt-3 font-mono text-xs text-black">Cited: {sourceIds.join(", ")}</p>}
        </div>
      ) : (
        <p className="mt-4 rounded-xl border border-black/15 bg-white px-4 py-3 text-sm text-black/70">The investigation narrative was not shown.</p>
      )}
    </section>
  );
}
