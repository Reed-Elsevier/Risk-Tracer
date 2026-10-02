import type { ReactNode } from "react";

export default function SignalCard({
  eyebrow,
  title,
  tone = "neutral",
  children
}: {
  eyebrow: string;
  title: string;
  tone?: "neutral" | "alert" | "watch" | "clear";
  children: ReactNode;
}) {
  const accents = {
    neutral: "border-slate-200",
    alert: "border-ember/40 bg-[#fff9f5]",
    watch: "border-gold/40 bg-[#fffcf4]",
    clear: "border-moss/30 bg-[#f6fbf6]"
  };
  return (
    <section className={`rounded-2xl border bg-white/80 p-5 shadow-card ${accents[tone]}`}>
      <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">{eyebrow}</p>
      <h2 className="mb-4 text-lg font-semibold tracking-tight text-ink">{title}</h2>
      {children}
    </section>
  );
}
