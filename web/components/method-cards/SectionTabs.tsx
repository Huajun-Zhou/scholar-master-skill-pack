"use client";

import { useRef, useEffect } from "react";

export interface SectionTab {
  id: string;
  label: string;
}

interface SectionTabsProps {
  sections: SectionTab[];
  activeSection: string;
  onSelect: (id: string) => void;
}

export function SectionTabs({
  sections,
  activeSection,
  onSelect,
}: SectionTabsProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLButtonElement>(null);

  // Auto-scroll active tab into view
  useEffect(() => {
    if (activeRef.current && containerRef.current) {
      const container = containerRef.current;
      const active = activeRef.current;
      const containerRect = container.getBoundingClientRect();
      const activeRect = active.getBoundingClientRect();

      if (
        activeRect.left < containerRect.left ||
        activeRect.right > containerRect.right
      ) {
        active.scrollIntoView({
          behavior: "smooth",
          block: "nearest",
          inline: "center",
        });
      }
    }
  }, [activeSection]);

  return (
    <div
      ref={containerRef}
      className="overflow-x-auto border-b border-[var(--border-subtle)] sticky top-0 z-20 bg-[var(--bg-base)]/90 backdrop-blur-md"
      style={{ scrollbarWidth: "none" }}
    >
      <div className="flex gap-0 min-w-max px-1">
        {sections.map((section) => {
          const isActive = section.id === activeSection;
          return (
            <button
              key={section.id}
              ref={isActive ? activeRef : undefined}
              onClick={() => onSelect(section.id)}
              className={`
                relative px-4 py-3 text-sm font-medium whitespace-nowrap transition-all duration-200
                ${
                  isActive
                    ? "text-[var(--color-gold)]"
                    : "text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
                }
              `}
            >
              {section.label}
              {/* Active indicator */}
              <span
                className={`
                  absolute bottom-0 left-2 right-2 h-0.5 rounded-full transition-all duration-300
                  ${isActive ? "bg-[var(--color-gold)]" : "bg-transparent"}
                `}
              />
            </button>
          );
        })}
      </div>
    </div>
  );
}
