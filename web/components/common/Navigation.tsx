"use client";

import { useState, useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Search } from "lucide-react";
import { useSearchUI } from "@/lib/search-index";

const navLinks = [
  { href: "/chat", label: "Chat" },
  { href: "/studio", label: "Studio" },
  { href: "/wiki", label: "Wiki" },
  { href: "/wiki/papers", label: "Papers" },
  { href: "/wiki/methods", label: "Methods" },
  { href: "/wiki/thinking-models", label: "Models" },
  { href: "/reports", label: "Reports" },
];

export function Navigation() {
  const pathname = usePathname();
  const [isDark, setIsDark] = useState(true);
  const [scrollY, setScrollY] = useState(0);
  const [scrollDirection, setScrollDirection] = useState<"up" | "down">("up");
  const lastScrollY = useRef(0);
  const rafId = useRef<number | null>(null);

  // Scroll-aware listener with requestAnimationFrame for performance
  useEffect(() => {
    const handleScroll = () => {
      if (rafId.current !== null) return;
      rafId.current = requestAnimationFrame(() => {
        const currentScrollY = window.scrollY;
        // Only update direction when scrolled past a 5px threshold to avoid flicker
        if (currentScrollY > lastScrollY.current + 5) {
          setScrollDirection("down");
        } else if (currentScrollY < lastScrollY.current - 5) {
          setScrollDirection("up");
        }
        lastScrollY.current = currentScrollY;
        setScrollY(currentScrollY);
        rafId.current = null;
      });
    };

    setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (rafId.current !== null) {
        cancelAnimationFrame(rafId.current);
      }
    };
  }, []);

  // Determine nav visual state
  const isAtTop = scrollY < 10;
  const isPastThreshold = scrollY > 50;
  const shouldHide = isPastThreshold && scrollDirection === "down";
  const isCompact = isPastThreshold;

  // Scroll class: hidden when scrolling down past 50px, visible otherwise (except at top)
  const scrollClass = isAtTop ? "" : shouldHide ? "nav-scroll-hidden" : "nav-scroll-visible";

  // On mount, check localStorage and apply theme
  useEffect(() => {
    const stored = localStorage.getItem("theme");
    // Default to dark; only switch to light if explicitly stored as "light"
    const dark = stored !== "light";
    setIsDark(dark);
    if (dark) {
      document.documentElement.classList.remove("light");
    } else {
      document.documentElement.classList.add("light");
    }
  }, []);

  const toggleTheme = () => {
    const next = !isDark;
    setIsDark(next);
    if (next) {
      document.documentElement.classList.remove("light");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.add("light");
      localStorage.setItem("theme", "light");
    }
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 h-14 ${isAtTop ? "" : "glass-nav"} ${scrollClass}`}
    >
      <div className="h-full max-w-[1440px] mx-auto px-4 sm:px-6 flex items-center justify-between">
        {/* Brand */}
        <Link
          href="/chat"
          className={`flex items-center group ${isCompact ? "gap-0" : "gap-2.5"}`}
        >
          <div className="w-7 h-7 rounded-lg bg-[var(--color-gold)]/15 border border-[var(--color-gold)]/20 flex items-center justify-center group-hover:bg-[var(--color-gold)]/20 transition-colors flex-shrink-0">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-[var(--color-gold)]"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          {/* Expanded brand text — fades and collapses in compact mode */}
          <div
            className={`hidden sm:flex flex-col transition-all duration-300 ease-in-out overflow-hidden whitespace-nowrap ${
              isCompact ? "max-w-0 opacity-0" : "max-w-[220px] opacity-100"
            }`}
          >
            <span className="text-sm font-semibold text-[var(--text-primary)] tracking-tight">
              Scholar Research Assistant
            </span>
            <span className="block text-xs font-serif italic text-[var(--color-gold)]">
              陈志远教授
            </span>
          </div>
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-0.5">
          {/* First 4 links: visible on tablet (sm+) */}
          {navLinks.slice(0, 4).map((link) => {
            const isActive =
              pathname === link.href || pathname?.startsWith(link.href + "/");
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`hidden sm:inline-flex px-3 py-1.5 rounded-lg text-xs font-medium tracking-wide transition-all duration-150 ${
                  isActive
                    ? "text-[var(--color-gold)] bg-[var(--color-gold)]/10 border border-[var(--border-accent)]"
                    : "text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
          {/* Last link (Models): visible on desktop (lg+) */}
          {navLinks.slice(4).map((link) => {
            const isActive =
              pathname === link.href || pathname?.startsWith(link.href + "/");
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`hidden lg:inline-flex px-3 py-1.5 rounded-lg text-xs font-medium tracking-wide transition-all duration-150 ${
                  isActive
                    ? "text-[var(--color-gold)] bg-[var(--color-gold)]/10 border border-[var(--border-accent)]"
                    : "text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]"
                }`}
              >
                {link.label}
              </Link>
            );
          })}

          {/* Search trigger */}
          <button
            onClick={() => useSearchUI.getState().open()}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-[var(--text-tertiary)] hover:text-[var(--color-gold)] hover:bg-[var(--color-gold)]/10 transition-all duration-150"
            aria-label="Open search"
          >
            <Search className="w-3.5 h-3.5" />
            <kbd className="hidden sm:inline-flex text-[10px] font-mono opacity-50 leading-none pt-px">
              ⌘K
            </kbd>
          </button>

          {/* Divider */}
          <div className="w-px h-5 bg-[var(--border-subtle)] mx-2" />

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="p-1.5 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] transition-all min-w-[36px] min-h-[36px] flex items-center justify-center"
            aria-label={isDark ? "切换到亮色模式" : "切换到暗色模式"}
            title={isDark ? "切换到亮色模式" : "切换到暗色模式"}
          >
            {isDark ? (
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
                <circle cx="12" cy="12" r="5" />
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
              </svg>
            ) : (
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
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            )}
          </button>
        </nav>
      </div>
    </header>
  );
}
