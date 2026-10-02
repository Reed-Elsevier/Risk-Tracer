import type { ReviewPriority } from "@/lib/types";

export default function PriorityBadge({ value }: { value: ReviewPriority }) {
  const styles: Record<ReviewPriority, string> = {
    High: "bg-[#f48529] text-black",
    Medium: "bg-[#e6b325] text-black",
    "No flagged signals": "bg-[#146b43] text-white"
  };
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] ${styles[value]}`}>
      {value}
    </span>
  );
}
