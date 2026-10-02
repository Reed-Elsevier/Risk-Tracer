"use client";

import Image from "next/image";
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
      <header className="border-b border-black/15 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-3 px-6 py-4">
          <Link href="/" className="flex items-center gap-3 rounded-lg">
            <Image
              src="/logo.webp"
              alt=""
              width={40}
              height={40}
              priority
              className="h-10 w-10 rounded-xl"
            />
            <span className="text-sm font-bold tracking-tight">RiskTracer</span>
          </Link>
          <nav aria-label="Primary">
            <Link
              href="/"
              aria-current={home ? "page" : undefined}
              className={`rounded-full px-3 py-1.5 text-sm font-semibold ${home ? "bg-black text-white" : "text-black hover:bg-black/5"}`}
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
