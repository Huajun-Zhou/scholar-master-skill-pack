"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useChatStore } from "@/lib/store";

const quickLinks = [
  { href: "/wiki/papers", label: "Papers", icon: "book" },
  { href: "/wiki/methods", label: "Methods", icon: "flask" },
  { href: "/wiki/thinking-models", label: "Thinking Models", icon: "brain" },
  { href: "/wiki", label: "Wiki", icon: "compass" },
  { href: "/wiki/timeline", label: "Timeline", icon: "clock" },
];

function LinkIcon({ icon }: { icon: string }) {
  switch (icon) {
    case "book":
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
      );
    case "flask":
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 3h6v5l4 10a2 2 0 0 1-1.7 3H6.7A2 2 0 0 1 5 18l4-10V3Z" />
          <path d="M9 3h6" />
          <path d="M7 13h10" />
        </svg>
      );
    case "brain":
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
        </svg>
      );
    case "clock":
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
      );
    default:
      return null;
  }
}

/* ------------------------------------------------------------------ */
/*  SidebarContent — shared between mobile, tablet, and desktop        */
/* ------------------------------------------------------------------ */

function SidebarContent({
  pathname,
  sessions,
  onClose,
  showCloseButton,
}: {
  pathname: string | null;
  sessions: { id: string; title: string; messageCount: number }[];
  onClose?: () => void;
  showCloseButton?: boolean;
}) {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Scholar info */}
      <div className="p-5 border-b border-[var(--border-subtle)]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[var(--color-gold)]/10 border border-[var(--color-gold)]/20 flex items-center justify-center">
            <span className="text-sm font-serif font-bold text-[var(--color-gold)]">
              陈
            </span>
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-sm font-semibold text-[var(--text-primary)] truncate">
              陈志远教授
            </h2>
            <p className="text-[0.65rem] text-[var(--text-tertiary)] truncate">
              Prof. Zhiyuan Chen · 通信安全
            </p>
          </div>
          {/* Close button — shown on mobile and tablet */}
          {showCloseButton && onClose && (
            <button
              onClick={onClose}
              className="p-1.5 -mr-1 rounded-lg text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-colors min-w-[36px] min-h-[36px] flex items-center justify-center"
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
          )}
        </div>
        <p className="text-[0.7rem] text-[var(--text-tertiary)] mt-2.5 leading-relaxed">
          15 篇公开论文 (2025-2026) · IIoT安全 · UAV通信 · 可信计算 · 隐私保护
        </p>
      </div>

      {/* API Key */}
      <ApiKeySection />
      {/* Quick links */}
      <div className="p-4 border-b border-[var(--border-subtle)]">
        <p className="text-[0.6rem] font-semibold uppercase tracking-widest text-[var(--text-tertiary)] mb-2.5 px-1">
          快速链接
        </p>
        <nav className="space-y-0.5">
          {quickLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={onClose}
                className={`
                  flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-all duration-150
                  ${
                    isActive
                      ? "text-[var(--color-gold)] bg-[var(--color-gold)]/8 border border-[var(--border-accent)]"
                      : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]"
                  }
                `}
              >
                <span className={`${isActive ? "text-[var(--color-gold)]" : "text-[var(--text-tertiary)]"}`}>
                  <LinkIcon icon={link.icon} />
                </span>
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Recent sessions */}
      <div className="flex-1 overflow-y-auto p-4">
        <p className="text-[0.6rem] font-semibold uppercase tracking-widest text-[var(--text-tertiary)] mb-2.5 px-1">
          最近会话
        </p>
        <div className="space-y-0.5">
          {sessions.map((session) => (
            <button
              key={session.id}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all text-left group"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="flex-shrink-0 text-[var(--text-tertiary)]"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <span className="truncate flex-1">{session.title}</span>
              <span className="text-[0.6rem] text-[var(--text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity">
                {session.messageCount}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-[var(--border-subtle)]">
        <p className="text-[0.55rem] text-[var(--text-tertiary)] text-center leading-relaxed">
          基于陈志远教授公开论文炼化 · 证据分级制度保障可追溯性
        </p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  ApiKeySection                                                       */
/* ------------------------------------------------------------------ */

function ApiKeySection() {
  const [key, setKey] = useState("");
  const [show, setShow] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("deepseek_api_key") || "";
      setKey(stored);
    } catch {}
  }, []);

  const save = () => {
    try {
      localStorage.setItem("deepseek_api_key", key.trim());
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {}
  };

  const clear = () => {
    setKey("");
    try { localStorage.removeItem("deepseek_api_key"); } catch {}
  };

  return (
    <div className="p-4 border-b border-[var(--border-subtle)]">
      <button
        onClick={() => setShow(!show)}
        className="flex items-center gap-2 w-full text-left group"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-[var(--text-tertiary)] group-hover:text-[var(--color-gold)] transition-colors">
          <circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
        <span className="text-[0.65rem] font-semibold uppercase tracking-wider text-[var(--text-tertiary)] group-hover:text-[var(--text-primary)] transition-colors">
          API Key {key ? "✓" : ""}
        </span>
      </button>
      {show && (
        <div className="mt-3 space-y-2">
          <input
            type="password"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder="sk-..."
            className="w-full px-3 py-2 text-xs bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:border-[var(--color-gold)]/50 transition-colors"
          />
          <div className="flex gap-2">
            <button
              onClick={save}
              className="flex-1 px-3 py-1.5 text-xs rounded-lg bg-[var(--color-gold)]/10 text-[var(--color-gold)] border border-[var(--color-gold)]/20 hover:bg-[var(--color-gold)]/20 transition-colors"
            >
              {saved ? "已保存 ✓" : "保存"}
            </button>
            <button
              onClick={clear}
              className="px-3 py-1.5 text-xs rounded-lg bg-transparent text-[var(--text-tertiary)] border border-[var(--border-subtle)] hover:text-[var(--text-primary)] transition-colors"
            >
              清除
            </button>
          </div>
          <p className="text-[0.55rem] text-[var(--text-tertiary)] leading-relaxed">
            输入你的 DeepSeek API Key，仅存储在浏览器本地，不会上传到服务器。
          </p>
        </div>
      )}
    </div>
  );
}

/* ================================================================== */
/*  Main Sidebar component                                            */
/* ================================================================== */

export function Sidebar() {
  const pathname = usePathname();
  const sessions = useChatStore((s) => s.sessions);
  const sidebarOpen = useChatStore((s) => s.sidebarOpen);
  const setSidebarOpen = useChatStore((s) => s.setSidebarOpen);
  const toggleSidebar = useChatStore((s) => s.toggleSidebar);

  // Close sidebar on navigation (mobile / tablet only)
  useEffect(() => {
    if (typeof window !== "undefined" && window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  // Body overflow prevention on mobile when sidebar is open
  useEffect(() => {
    if (sidebarOpen && typeof window !== "undefined" && window.innerWidth < 640) {
      document.body.classList.add("sidebar-open");
    } else {
      document.body.classList.remove("sidebar-open");
    }
    return () => document.body.classList.remove("sidebar-open");
  }, [sidebarOpen]);

  // Swipe gesture for mobile — detect swipes from left edge
  useEffect(() => {
    if (typeof window === "undefined") return;

    let touchStartX = 0;
    let touchStartY = 0;
    let touchStartTime = 0;

    const handleTouchStart = (e: TouchEvent) => {
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
      touchStartTime = Date.now();
    };

    const handleTouchEnd = (e: TouchEvent) => {
      const deltaX = e.changedTouches[0].clientX - touchStartX;
      const deltaY = e.changedTouches[0].clientY - touchStartY;
      const elapsed = Date.now() - touchStartTime;

      // Must be a quick gesture (< 400ms) and sufficiently horizontal
      if (elapsed > 400) return;
      if (Math.abs(deltaX) < Math.abs(deltaY) * 1.5) return;

      if (!sidebarOpen && touchStartX < 25 && deltaX > 80) {
        // Swipe right from left edge → open sidebar
        setSidebarOpen(true);
      } else if (sidebarOpen && deltaX < -60) {
        // Swipe left → close sidebar
        setSidebarOpen(false);
      }
    };

    document.addEventListener("touchstart", handleTouchStart, { passive: true });
    document.addEventListener("touchend", handleTouchEnd, { passive: true });

    return () => {
      document.removeEventListener("touchstart", handleTouchStart);
      document.removeEventListener("touchend", handleTouchEnd);
    };
  }, [sidebarOpen, setSidebarOpen]);

  return (
    <>
      {/* ─── Desktop sidebar — always visible on lg+ ─── */}
      <aside className="hidden lg:flex fixed top-14 left-0 z-20 h-[calc(100vh-3.5rem)] w-[320px] glass-sidebar flex-col overflow-hidden">
        <SidebarContent pathname={pathname} sessions={sessions} />
      </aside>

      {/* ─── Tablet sidebar — collapsible on sm..lg ─── */}
      <aside
        className={[
          "hidden sm:flex lg:hidden",
          "fixed top-14 left-0 z-20",
          "h-[calc(100vh-3.5rem)]",
          "glass-sidebar",
          "border-r border-[var(--border-subtle)]",
          "flex-col overflow-hidden",
          "transition-all duration-300 ease-in-out",
          sidebarOpen ? "w-[240px]" : "w-0 border-r-0",
        ].join(" ")}
      >
        <div
          className={`flex flex-col h-full w-[240px] flex-shrink-0 ${
            !sidebarOpen ? "invisible" : ""
          }`}
        >
          <SidebarContent
            pathname={pathname}
            sessions={sessions}
            onClose={toggleSidebar}
            showCloseButton
          />
        </div>
      </aside>

      {/* ─── Toggle button (hamburger / close) — visible below lg ─── */}
      <button
        onClick={toggleSidebar}
        className="fixed top-14 left-0 z-40 p-2 m-2 rounded-lg lg:hidden text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] transition-colors min-tap-target flex items-center justify-center"
        aria-label={sidebarOpen ? "关闭侧边栏" : "打开侧边栏"}
      >
        {sidebarOpen ? (
          /* X icon when sidebar is open */
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        ) : (
          /* Hamburger icon when sidebar is closed */
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        )}
      </button>

      {/* ─── Mobile overlay ─── */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            key="mobile-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-30 bg-black/60 sm:hidden"
            onClick={toggleSidebar}
          />
        )}
      </AnimatePresence>

      {/* ─── Mobile drawer ─── */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            key="mobile-drawer"
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 300 }}
            className="fixed top-14 left-0 z-30 h-[calc(100vh-3.5rem)] w-[280px] glass-sidebar flex flex-col overflow-hidden sm:hidden"
          >
            <SidebarContent
              pathname={pathname}
              sessions={sessions}
              onClose={toggleSidebar}
              showCloseButton
            />
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
