import type { ReactNode } from "react";

export default function SignalCard({
  eyebrow,
  title,
  tone = "neutral",
  children
}: {
  eyebrow: string;
  title: string;
  tone?: "neutral" | "alert" | "watch" | "clear" | "record";
  children: ReactNode;
}) {
  const accents = {
    neutral: "border-black/15 bg-white",
    alert: "border-[#f48529] bg-[#fff3e8]",
    watch: "border-[#e6b325] bg-[#fbf4dc]",
    clear: "border-[#146b43] bg-[#e8f5ee]",
    record: "border-[#1e4e8c] bg-[#eef3fa]"
  };
  const labels = {
    neutral: "text-black",
    alert: "text-[#9a4a12]",
    watch: "text-[#7a5b00]",
    clear: "text-[#146b43]",
    record: "text-[#1e4e8c]"
  };
  return (
    <section className={`rounded-2xl border p-5 shadow-card ${accents[tone]}`}>
      <p className={`mb-2 text-[11px] font-bold uppercase tracking-[0.18em] ${labels[tone]}`}>{eyebrow}</p>
      <h2 className="mb-4 text-lg font-semibold tracking-tight text-ink">{title}</h2>
      {children}
    </section>
  );
}
