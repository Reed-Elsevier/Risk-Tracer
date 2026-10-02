"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import InvoiceSearch from "@/components/InvoiceSearch";

export default function AppShell({
  children,
  search = true
}: {
  children: ReactNode;
  search?: boolean;
}) {
  const pathname = usePathname();
  const home = pathname === "/";

  return (
    <div className="min-h-screen bg-paper text-ink">
      <header className="border-b border-[#d5ddd6] bg-paper">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-3 px-6 py-4">
          <Link href="/" className="flex items-center gap-3 rounded-lg">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-ink text-sm font-black text-[#d7efe0]">R</span>
            <span className="text-sm font-black tracking-tight">RiskTracer</span>
          </Link>
          <nav aria-label="Primary">
            <Link
              href="/"
              aria-current={home ? "page" : undefined}
              className={`rounded-full px-3 py-1.5 text-sm font-semibold ${home ? "bg-ink text-[#d7efe0]" : "text-ink hover:bg-mist"}`}
            >
              Home
            </Link>
          </nav>
          {search ? (
            <div className="w-full sm:ml-auto sm:w-80">
              <InvoiceSearch />
            </div>
          ) : null}
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
