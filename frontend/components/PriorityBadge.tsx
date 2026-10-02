import type { ReviewPriority } from "@/lib/types";

export default function PriorityBadge({ value }: { value: ReviewPriority }) {
  const styles: Record<ReviewPriority, string> = {
    High: "bg-ember text-white",
    Medium: "bg-gold text-white",
    "No flagged signals": "bg-mist text-ink"
  };
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] ${styles[value]}`}>
      {value}
    </span>
  );
}
