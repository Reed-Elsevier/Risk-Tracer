import type { EvidenceSentence } from "@/lib/types";

function SourceId({ value }: { value: string }) {
  return (
    <a href={`#source-${value}`} className="rounded-md bg-[#1e4e8c] px-1.5 py-0.5 font-mono text-[11px] font-semibold text-white hover:bg-black">
      {value}
    </a>
  );
}

export default function EvidenceBrief({
  sentences,
  suggestedNextStep,
  retrospective
}: {
  sentences: EvidenceSentence[];
  suggestedNextStep: string;
  retrospective: boolean;
}) {
  return (
    <section className="rounded-2xl border border-black/15 bg-white p-5 shadow-card">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-black/60">Evidence brief</p>
          <h2 className="text-xl font-semibold tracking-tight text-ink">What the records say</h2>
        </div>
        <span className="rounded-full bg-[#1e4e8c] px-3 py-1 text-xs font-semibold text-white">
          {retrospective ? "Retrospective review" : "Pre-payment review"}
        </span>
      </div>
      <div className="space-y-4">
        {sentences.map((sentence, index) => (
          <div key={`${sentence.text}-${index}`} className="rounded-xl bg-[#eef3fa] px-4 py-3 text-sm leading-6 text-black">
            {sentence.source_ids.map((sourceId) => <span key={`anchor-${sourceId}`} id={`source-${sourceId}`} className="scroll-mt-24" aria-hidden="true" />)}
            <p>{sentence.text}</p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {sentence.source_ids.map((sourceId) => <SourceId key={sourceId} value={sourceId} />)}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 rounded-xl bg-ink p-4 text-sm leading-6 text-white">
        <span className="mr-2 font-semibold text-[#f48529]">Suggested next step</span>
        {suggestedNextStep}
      </div>
    </section>
  );
}
