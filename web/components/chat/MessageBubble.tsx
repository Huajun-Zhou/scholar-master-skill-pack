"use client";

import { motion } from "framer-motion";
import * as Tooltip from "@radix-ui/react-tooltip";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import type { Message } from "@/lib/store";

const USER_AVATAR_INITIALS = "你";
const ASSISTANT_AVATAR_INITIALS = "S";

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
  isFirstAnswer?: boolean;
}

/* Spring transition configs */
const springUser = { type: "spring" as const, stiffness: 300, damping: 25 };
const springAssistant = { type: "spring" as const, stiffness: 300, damping: 25 };

/* Staggered children — 0.1s between items */
const staggerContainer = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.1, delayChildren: 0.1 },
  },
};

const staggerItem = {
  hidden: { opacity: 0, y: 8 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: "easeOut" as const },
  },
};

export function MessageBubble({ message, isStreaming = false, isFirstAnswer = false }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 30 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={isUser ? springUser : springAssistant}
      className={`flex gap-3 sm:gap-4 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* Avatar */}
      <div
        className={`
          flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
          text-[0.7rem] font-semibold font-mono tracking-wider
          transition-all duration-300
          ${isUser
            ? "bg-[var(--bg-elevated)] text-[var(--text-secondary)] border border-[var(--border-default)]"
            : isStreaming
              ? "bg-[var(--color-gold)]/15 text-[var(--color-gold)] border border-[var(--color-gold)]/20 animate-glow-gold"
              : "bg-[var(--color-gold)]/15 text-[var(--color-gold)] border border-[var(--color-gold)]/20"
          }
        `}
      >
        {isUser ? USER_AVATAR_INITIALS : ASSISTANT_AVATAR_INITIALS}
      </div>

      {/* Content */}
      <div className={`flex flex-col gap-1.5 max-w-[90%] sm:max-w-[80%] lg:max-w-[75%] ${isUser ? "items-end" : "items-start"}`}>
        {/* Header */}
        <div className={`flex items-center gap-2 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
          <span className="text-[0.7rem] font-medium text-[var(--text-tertiary)] tracking-wide uppercase">
            {isUser ? "You" : "Scholar"}
          </span>
          {isUser && (
            <span className="text-[0.65rem] text-[var(--text-tertiary)]">
              {new Date(message.timestamp).toLocaleTimeString("zh-CN", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          )}
        </div>

        {/* Bubble */}
        <div
          className={`
            rounded-2xl px-4 py-3 text-sm leading-relaxed
            ${
              isUser
                ? "bg-[var(--color-gold)]/10 border border-[var(--color-gold)]/15 text-[var(--text-primary)] rounded-tr-md msg-bubble-user"
                : "bg-[var(--bg-surface)] border border-[var(--border-subtle)] rounded-tl-md msg-bubble-assistant"
            }
            ${!isUser && isFirstAnswer ? "msg-first-answer" : ""}
          `}
        >
          {/* Assistant header with gold accent */}
          {!isUser && (
            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-[var(--border-subtle)]">
              <span className="text-[0.65rem] font-semibold uppercase tracking-wider text-[var(--color-gold)]">
                Scholar Research Assistant
              </span>
              <span className="text-[0.6rem] text-[var(--text-tertiary)]">
                {new Date(message.timestamp).toLocaleTimeString("zh-CN", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          )}

          {/* Main content */}
          <div className="text-[var(--text-primary)]">
            <MarkdownRenderer content={message.content} />
          </div>

          {/* Streaming indicator */}
          {isStreaming && (
            <span className="inline-flex ml-0.5">
              <span className="w-1.5 h-3.5 bg-[var(--color-gold)] rounded-full animate-pulse-subtle" />
            </span>
          )}

          {/* Evidence sections — staggered entrance */}
          {!isUser && message.evidenceSections && message.evidenceSections.length > 0 && (
            <motion.div
              className="mt-4 pt-3 border-t border-[var(--border-subtle)] space-y-2"
              variants={staggerContainer}
              initial="hidden"
              animate="show"
            >
              <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
                证据来源
              </p>
              {message.evidenceSections.map((section, idx) => (
                <motion.div
                  key={idx}
                  variants={staggerItem}
                  className={`evidence-section evidence-section--${section.level.toLowerCase()}`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`evidence-badge evidence-badge--${section.level.toLowerCase()}`}
                    >
                      [{section.level}]
                    </span>
                    <span className="text-xs font-medium text-[var(--text-secondary)]">
                      {section.title}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                    {section.content}
                  </p>
                  {section.papers.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {section.papers.map((paper, pid) => (
                        <span
                          key={pid}
                          className="text-[0.6rem] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-tertiary)] border border-[var(--border-subtle)]"
                        >
                          {paper}
                        </span>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* Source paper chips — with tooltip + hover effects */}
          {!isUser && message.sourcePapers && message.sourcePapers.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              <Tooltip.Provider delayDuration={400}>
                {message.sourcePapers.map((paper) => (
                  <Tooltip.Root key={paper.id}>
                    <Tooltip.Trigger asChild>
                      <span
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full
                          bg-[var(--bg-hover)] border border-[var(--border-accent)]
                          text-[0.65rem] font-mono text-[var(--color-gold-dim)]
                          hover:bg-[var(--border-accent)] hover:text-[var(--color-gold)]
                          hover:border-[var(--color-gold)]/40 hover:scale-105
                          transition-all duration-200 cursor-pointer"
                      >
                        <svg
                          width="10"
                          height="10"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="opacity-60"
                        >
                          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                        </svg>
                        {paper.id}
                      </span>
                    </Tooltip.Trigger>
                    {paper.title && (
                      <Tooltip.Portal>
                        <Tooltip.Content
                          side="top"
                          align="center"
                          sideOffset={6}
                          className="max-w-xs z-50 px-3 py-1.5 rounded-lg text-xs leading-relaxed"
                          data-radix-tooltip-content
                        >
                          {paper.title}
                          <Tooltip.Arrow className="fill-[var(--bg-elevated)]" />
                        </Tooltip.Content>
                      </Tooltip.Portal>
                    )}
                  </Tooltip.Root>
                ))}
              </Tooltip.Provider>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
