"use client";

import { useState, useMemo, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { WikiTreeSidebar } from "@/components/wiki/WikiTreeSidebar";
import { PageTransition } from "@/components/common/PageTransition";

/** Mapping of URL slugs to human-readable display names for breadcrumbs. */
const BREADCRUMB_LABELS: Record<string, string> = {
  wiki: "Wiki",
  papers: "论文",
  methods: "方法卡片",
  "thinking-models": "思维模型",
  timeline: "研究时间线",
  concepts: "核心概念",
  synthesis: "综合分析",
};

/** Build breadcrumb segments from the current pathname. */
function useBreadcrumbs() {
  const pathname = usePathname();

  return useMemo(() => {
    if (!pathname) return [];

    const segments = pathname.split("/").filter(Boolean);
    const crumbs: { label: string; href: string }[] = [];

    // Always start with Wiki
    crumbs.push({ label: "Wiki", href: "/wiki" });

    let cumulative = "";
    for (let i = 1; i < segments.length; i++) {
      const seg = segments[i];
      cumulative += `/${seg}`;

      // Use the label mapping, or fall back to a formatted version of the slug
      const label =
        BREADCRUMB_LABELS[seg] ??
        decodeURIComponent(seg)
          .replace(/-/g, " ")
          .replace(/_/g, " ")
          .replace(/\b\w/g, (c) => c.toUpperCase());

      crumbs.push({ label, href: cumulative });
    }

    return crumbs;
  }, [pathname]);
}

export default function WikiLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const breadcrumbs = useBreadcrumbs();
  const pathname = usePathname();

  // Close sidebar after navigation on mobile
  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  return (
    <div className="flex min-h-screen bg-[var(--bg-base)]">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Wiki sidebar (left, 280px) */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-[280px]
          glass-sidebar
          transition-transform duration-300 ease-out
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          lg:relative lg:translate-x-0 lg:z-0 lg:flex-shrink-0
          flex flex-col overflow-hidden
        `}
      >
        <WikiTreeSidebar />

        {/* Mobile close button inside sidebar */}
        <button
          onClick={() => setSidebarOpen(false)}
          className="absolute top-3 right-3 p-1.5 rounded-md text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] lg:hidden transition-colors min-w-[36px] min-h-[36px] flex items-center justify-center"
          aria-label="关闭侧边栏"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar with breadcrumbs and mobile toggle */}
        <header className="sticky top-0 z-30 h-12 glass-nav">
          <div className="h-full flex items-center gap-3 px-4 sm:px-6">
            {/* Mobile sidebar toggle */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 -ml-1 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] lg:hidden transition-colors min-w-[36px] min-h-[36px] flex items-center justify-center"
              aria-label="打开侧边栏"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            </button>

            {/* Breadcrumbs */}
            <nav className="flex items-center gap-1.5 text-xs min-w-0" aria-label="Breadcrumb">
              {breadcrumbs.map((crumb, index) => (
                <span key={crumb.href} className="flex items-center gap-1.5 min-w-0">
                  {index > 0 && (
                    <svg
                      width="10"
                      height="10"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="flex-shrink-0 text-[var(--text-tertiary)] opacity-40"
                    >
                      <path d="m9 18 6-6-6-6" />
                    </svg>
                  )}
                  {index < breadcrumbs.length - 1 ? (
                    <Link
                      href={crumb.href}
                      className="text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors truncate"
                    >
                      {crumb.label}
                    </Link>
                  ) : (
                    <span className="text-[var(--color-gold)] font-medium truncate">
                      {crumb.label}
                    </span>
                  )}
                </span>
              ))}
            </nav>
          </div>
        </header>

        {/* Page content with transition */}
        <main className="flex-1">
          <PageTransition>{children}</PageTransition>
        </main>
      </div>
    </div>
  );
}
