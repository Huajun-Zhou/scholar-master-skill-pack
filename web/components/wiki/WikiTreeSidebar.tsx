"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import * as Collapsible from "@radix-ui/react-collapsible";

interface WikiSection {
  title: string;
  icon: string;
  slug: string;
  items?: { label: string; slug: string }[];
}

const WIKI_SECTIONS: WikiSection[] = [
  {
    title: "Papers",
    icon: "book",
    slug: "/wiki/papers",
    items: [
      { label: "All Papers", slug: "/wiki/papers" },
    ],
  },
  {
    title: "Methods",
    icon: "flask",
    slug: "/wiki/methods",
    items: [
      { label: "All Methods", slug: "/wiki/methods" },
    ],
  },
  {
    title: "Thinking Models",
    icon: "brain",
    slug: "/wiki/thinking-models",
  },
  {
    title: "Concepts",
    icon: "compass",
    slug: "/wiki",
    items: [
      { label: "Glossary", slug: "/wiki/glossary" },
      { label: "Research Questions", slug: "/wiki/research_questions" },
      { label: "Open Questions", slug: "/wiki/open_questions" },
      { label: "Limitations", slug: "/wiki/limitations" },
      { label: "Contradictions", slug: "/wiki/contradictions" },
    ],
  },
  {
    title: "Synthesis",
    icon: "layers",
    slug: "/wiki",
    items: [
      { label: "Evidence Standards", slug: "/wiki/synthesis/evidence_standards" },
      { label: "Problem Framing", slug: "/wiki/synthesis/problem_framing_patterns" },
      { label: "Method Evolution", slug: "/wiki/synthesis/method_evolution" },
      { label: "Research Lines", slug: "/wiki/synthesis/research_lines" },
      { label: "Research Playbook", slug: "/wiki/synthesis/research_playbook" },
    ],
  },
  {
    title: "Research Paradigm",
    icon: "target",
    slug: "/wiki/research_paradigm",
  },
  {
    title: "Timeline",
    icon: "clock",
    slug: "/wiki/timeline",
  },
];

function SectionIcon({ icon, isActive }: { icon: string; isActive: boolean }) {
  const className = `w-4 h-4 ${isActive ? "text-[var(--color-gold)]" : "text-[var(--text-tertiary)]"}`;

  switch (icon) {
    case "book":
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
      );
    case "flask":
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
          <path d="M9 3h6v5l4 10a2 2 0 0 1-1.7 3H6.7A2 2 0 0 1 5 18l4-10V3Z" />
          <path d="M9 3h6" />
          <path d="M7 13h10" />
        </svg>
      );
    case "brain":
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
          <path d="M12 4.5a6 6 0 0 1 6 6c0 2.5-1 4.5-2.5 6" />
          <path d="M12 4.5a6 6 0 0 0-6 6c0 2.5 1 4.5 2.5 6" />
          <path d="M9.5 21c.5.5 1.5.5 2.5.5s2 0 2.5-.5" />
          <path d="M8 11.5c0 1.5.5 2.5 1 3.5" />
          <path d="M16 11.5c0 1.5-.5 2.5-1 3.5" />
          <path d="M12 2v2.5" />
        </svg>
      );
    case "compass":
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
          <circle cx="12" cy="12" r="10" />
          <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
        </svg>
      );
    case "layers":
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
          <polygon points="12 2 2 7 12 12 22 7 12 2" />
          <polyline points="2 17 12 22 22 17" />
          <polyline points="2 12 12 17 22 12" />
        </svg>
      );
    case "target":
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
          <circle cx="12" cy="12" r="10" />
          <circle cx="12" cy="12" r="6" />
          <circle cx="12" cy="12" r="2" />
        </svg>
      );
    case "clock":
      return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
      );
    default:
      return null;
  }
}

export function WikiTreeSidebar() {
  const pathname = usePathname();
  const [searchQuery, setSearchQuery] = useState("");

  // Determine which sections should be open by default based on current path
  const getDefaultOpenSections = useCallback((): string[] => {
    if (!pathname) return [];
    const open: string[] = [];
    for (const section of WIKI_SECTIONS) {
      if (section.items) {
        const isChildActive = section.items.some(
          (item) => pathname === item.slug || pathname.startsWith(item.slug + "/")
        );
        if (isChildActive) open.push(section.title);
      }
    }
    return open;
  }, [pathname]);

  const [openSections, setOpenSections] = useState<string[]>(getDefaultOpenSections);

  const isActive = (slug: string) => pathname === slug || pathname.startsWith(slug + "/");

  const toggleSection = (title: string) => {
    setOpenSections((prev) =>
      prev.includes(title)
        ? prev.filter((t) => t !== title)
        : [...prev, title]
    );
  };

  // Simple filter for pages
  const filteredSections = WIKI_SECTIONS.filter((section) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    if (section.title.toLowerCase().includes(q)) return true;
    if (section.items) {
      return section.items.some((item) => item.label.toLowerCase().includes(q));
    }
    return false;
  });

  return (
    <aside className="w-full h-full flex flex-col">
      {/* Scholar branding */}
      <div className="p-4 border-b border-[var(--border-subtle)]">
        <Link
          href="/wiki"
          className="flex items-center gap-2.5 group"
        >
          <div className="w-8 h-8 rounded-lg bg-[var(--color-gold)]/10 border border-[var(--color-gold)]/20 flex items-center justify-center group-hover:bg-[var(--color-gold)]/20 transition-colors">
            <span className="text-xs font-serif font-bold text-[var(--color-gold)]">
              W
            </span>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[var(--text-primary)] group-hover:text-[var(--color-gold)] transition-colors">
              Scholar Wiki
            </h2>
            <p className="text-[0.55rem] text-[var(--text-tertiary)]">
              陈志远教授 · 学术知识库
            </p>
          </div>
        </Link>
      </div>

      {/* Search box — for later Phase 4 Cmd+K integration */}
      <div className="px-4 pt-3 pb-2">
        <div className="relative">
          <svg
            className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--text-tertiary)] pointer-events-none"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search wiki... (Cmd+K)"
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--color-gold)]/40 focus:ring-1 focus:ring-[var(--color-gold)]/20 transition-all"
          />
        </div>
      </div>

      {/* Navigation tree */}
      <nav className="flex-1 overflow-y-auto px-2 pb-4">
        <div className="space-y-0.5">
          {filteredSections.map((section) => {
            const sectionActive = isActive(section.slug);
            const hasItems = section.items && section.items.length > 0;
            const isOpen = openSections.includes(section.title);

            if (!hasItems) {
              // Leaf node
              return (
                <Link
                  key={section.slug}
                  href={section.slug}
                  className={`
                    flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-all duration-150
                    ${
                      sectionActive
                        ? "text-[var(--color-gold)] bg-[var(--color-gold)]/8 border border-[var(--border-accent)]"
                        : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]"
                    }
                  `}
                >
                  <SectionIcon icon={section.icon} isActive={sectionActive} />
                  <span className="font-medium">{section.title}</span>
                </Link>
              );
            }

            // Branch node with collapsible children
            return (
              <Collapsible.Root
                key={section.title}
                open={isOpen}
                onOpenChange={() => toggleSection(section.title)}
              >
                <Collapsible.Trigger asChild>
                  <button
                    className={`
                      w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-all duration-150 group
                      ${
                        sectionActive
                          ? "text-[var(--color-gold)] bg-[var(--color-gold)]/8 border border-[var(--border-accent)]"
                          : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]"
                      }
                    `}
                  >
                    {/* Chevron */}
                    <svg
                      width="10"
                      height="10"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className={`flex-shrink-0 transition-transform duration-200 ${
                        isOpen ? "rotate-90" : ""
                      } ${
                        sectionActive
                          ? "text-[var(--color-gold)]"
                          : "text-[var(--text-tertiary)]"
                      }`}
                    >
                      <path d="m9 18 6-6-6-6" />
                    </svg>
                    <SectionIcon icon={section.icon} isActive={sectionActive} />
                    <span className="font-medium">{section.title}</span>
                  </button>
                </Collapsible.Trigger>

                <Collapsible.Content className="overflow-hidden data-[state=closed]:animate-collapse-up data-[state=open]:animate-collapse-down">
                  <div className="ml-3 pl-3 border-l border-[var(--border-subtle)] mt-0.5 space-y-0.5">
                    {section.items!.map((item) => {
                      const itemActive = pathname === item.slug;
                      return (
                        <Link
                          key={item.slug}
                          href={item.slug}
                          className={`
                            flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs transition-all duration-150
                            ${
                              itemActive
                                ? "text-[var(--color-gold)] bg-[var(--color-gold)]/6 border border-[var(--border-accent)]"
                                : "text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]"
                            }
                          `}
                        >
                          <span className="w-1 h-1 rounded-full bg-current opacity-40 flex-shrink-0" />
                          <span>{item.label}</span>
                        </Link>
                      );
                    })}
                  </div>
                </Collapsible.Content>
              </Collapsible.Root>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-[var(--border-subtle)]">
        <Link
          href="/chat"
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-[0.65rem] text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all"
        >
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          Back to Chat
        </Link>
      </div>
    </aside>
  );
}
