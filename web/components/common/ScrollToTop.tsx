"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { usePathname } from "next/navigation";

/**
 * A floating scroll-to-top button that appears after scrolling down 500px.
 * Works on wiki pages (window scroll) and chat pages (inner scroll container).
 * Uses framer-motion for fade in/out and respects prefers-reduced-motion.
 */
export function ScrollToTop() {
  const [visible, setVisible] = useState(false);
  const pathname = usePathname();
  const prefersReducedMotion = useReducedMotion();

  // Only show on chat and wiki pages (not the welcome screen, which redirects anyway)
  const isEnabled =
    pathname?.startsWith("/chat") || pathname?.startsWith("/wiki");

  // Use a ref to hold a reference to the chat scroll container so we can
  // clean up its event listener properly
  const chatContainerRef = useRef<Element | null>(null);

  useEffect(() => {
    if (!isEnabled) {
      setVisible(false);
      return;
    }

    // The chat page uses an inner overflow-y-auto container for scroll.
    // We detect it by looking for the first element with that class.
    const chatContainer = document.querySelector(".overflow-y-auto");
    chatContainerRef.current = chatContainer;

    const handleScroll = () => {
      const scrollPos = chatContainer
        ? chatContainer.scrollTop
        : window.scrollY;
      setVisible(scrollPos > 500);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    if (chatContainer) {
      chatContainer.addEventListener("scroll", handleScroll, {
        passive: true,
      });
    }

    // Set initial state
    handleScroll();

    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (chatContainer) {
        chatContainer.removeEventListener("scroll", handleScroll);
      }
    };
  }, [isEnabled]);

  const scrollToTop = () => {
    const container = chatContainerRef.current;
    if (container) {
      container.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <AnimatePresence>
      {visible && isEnabled && (
        <motion.button
          key="scroll-to-top"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={
            prefersReducedMotion
              ? { opacity: 1, scale: 1 }
              : { opacity: 1, scale: 1 }
          }
          exit={
            prefersReducedMotion
              ? { opacity: 0, scale: 1 }
              : { opacity: 0, scale: 0.8 }
          }
          transition={{ duration: 0.2, ease: "easeOut" }}
          onClick={scrollToTop}
          className="fixed bottom-6 right-6 z-40 w-10 h-10 rounded-full bg-[var(--color-gold)]/15 border border-[var(--color-gold)]/25 flex items-center justify-center cursor-pointer hover:bg-[var(--color-gold)]/25 hover:border-[var(--color-gold)]/40 transition-colors shadow-lg backdrop-blur-sm"
          aria-label="返回顶部"
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
            className="text-[var(--color-gold)]"
          >
            <path d="m18 15-6-6-6 6" />
          </svg>
        </motion.button>
      )}
    </AnimatePresence>
  );
}
