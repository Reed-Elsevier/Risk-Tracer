import { Sparkles } from "lucide-react";

type NarrativeBlock =
  | { kind: "heading"; text: string }
  | { kind: "paragraph"; text: string }
  | { kind: "list"; items: string[] };

function parseNarrative(text: string): NarrativeBlock[] {
  const blocks: NarrativeBlock[] = [];
  let listItems: string[] = [];

  function flushList() {
    if (listItems.length > 0) {
      blocks.push({ kind: "list", items: listItems });
      listItems = [];
    }
  }

  for (const line of text.split(/\r?\n/).map((value) => value.trim())) {
    if (!line) {
      flushList();
    } else if (line.startsWith("## ")) {
      flushList();
      blocks.push({ kind: "heading", text: line.slice(3) });
    } else if (line.startsWith("- ")) {
      listItems.push(line.slice(2));
    } else {
      flushList();
      blocks.push({ kind: "paragraph", text: line });
    }
  }
  flushList();
  return blocks;
}

export default function InvestigationNarrative({
  status,
  text,
  sourceIds
}: {
  status: "shown" | "unavailable";
  text: string;
  sourceIds: string[];
}) {
  const blocks = parseNarrative(text);

  return (
    <section id="ai-narrative" className="overflow-hidden rounded-2xl border border-black/15 bg-white shadow-card">
      <header className="flex flex-wrap items-start justify-between gap-4 p-5 sm:p-6">
        <div className="max-w-2xl">
          <h2 className="text-xl font-bold tracking-tight text-ink">AI investigation narrative</h2>
          <p className="mt-1 text-sm leading-6 text-black/65">
            A grounded reading of the cited records. It does not set review priority or make the decision.
          </p>
        </div>
        {status === "shown" && (
          <span className="inline-flex items-center gap-2 rounded-full bg-[#1e4e8c] px-3 py-1.5 text-xs font-semibold text-white">
            <Sparkles size={14} aria-hidden="true" />
            Generated now
          </span>
        )}
      </header>
      {status === "shown" ? (
        <>
          <article className="border-y border-[#cbd8e8] bg-[#f5f8fc] px-5 py-6 sm:px-6">
            <div className="max-w-[75ch] space-y-4 text-[15px] leading-7 text-black/80">
              {blocks.map((block, index) => {
                if (block.kind === "heading") {
                  return <h3 key={`${block.text}-${index}`} className="pt-2 text-base font-bold tracking-tight text-black first:pt-0">{block.text}</h3>;
                }
                if (block.kind === "list") {
                  return (
                    <ul key={`list-${index}`} className="space-y-2 pl-5">
                      {block.items.map((item) => <li key={item} className="list-disc pl-1 marker:text-[#1e4e8c]">{item}</li>)}
                    </ul>
                  );
                }
                return <p key={`${block.text}-${index}`}>{block.text}</p>;
              })}
            </div>
          </article>
          {sourceIds.length > 0 && (
            <footer className="p-5 sm:px-6">
              <h3 className="text-sm font-bold text-black">Sources used</h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {sourceIds.map((sourceId) => (
                  <a
                    key={sourceId}
                    href={`#source-${sourceId}`}
                    className="rounded-md bg-[#eef3fa] px-2 py-1 font-mono text-[11px] font-semibold text-[#1e4e8c] underline-offset-2 hover:underline"
                  >
                    {sourceId}
                  </a>
                ))}
              </div>
            </footer>
          )}
        </>
      ) : (
        <div className="border-t border-black/10 px-5 py-5 sm:px-6">
          <p className="text-sm text-black/70">The investigation narrative was not shown. Continue with the evidence brief below.</p>
        </div>
      )}
    </section>
  );
}
