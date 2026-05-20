"use client";

import { useRef, useEffect, useCallback, useState } from "react";
import {
  motion,
  AnimatePresence,
  useAnimation,
  useReducedMotion,
} from "framer-motion";
import * as Tooltip from "@radix-ui/react-tooltip";
import {
  FlaskConical,
  Lightbulb,
  GitBranch,
  FileSearch,
} from "lucide-react";
import { useChatStore, type Message } from "@/lib/store";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { InputBar } from "@/components/chat/InputBar";
import { AnswerSkeleton } from "@/components/chat/AnswerSkeleton";

/* ================================================================== */
/*  First-message helpers                                              */
/* ================================================================== */

function hasAskedBefore(): boolean {
  if (typeof window === "undefined") return true;
  try {
    return localStorage.getItem("scholar_has_asked") === "true";
  } catch {
    return true;
  }
}

function markAsked() {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem("scholar_has_asked", "true");
  } catch {
    // Silently fail
  }
}

/* ================================================================== */
/*  Constants                                                          */
/* ================================================================== */

const TITLE = "Scholar Research Assistant";

const EXAMPLE_QUESTIONS = [
  {
    label: "隐私保护",
    question: "陈志远教授在隐私保护协作学习方面有哪些核心贡献？",
    description: "了解联邦学习与密码学融合的前沿方法",
    icon: FlaskConical,
  },
  {
    label: "方法迁移",
    question: "如何将混合安全计算架构迁移到医疗数据隐私保护？",
    description: "探索跨领域安全方案迁移路径",
    icon: GitBranch,
  },
  {
    label: "UAV安全",
    question: "无人机蜂群的安全通信应该如何设计？",
    description: "分析物理层安全与MARL的结合方案",
    icon: Lightbulb,
  },
  {
    label: "论文审查",
    question: "如何按安全实证标准审查通信安全论文？",
    description: "获取系统化安全论文评审方法论",
    icon: FileSearch,
  },
];

const STATS = [
  { icon: "📄", label: "论文", value: "15篇" },
  { icon: "🔬", label: "方法卡", value: "7张" },
  { icon: "🧠", label: "思维模型", value: "6个" },
  { icon: "📊", label: "证据", value: "~300条" },
];

const EVIDENCE_ITEMS = [
  {
    label: "A",
    title: "直接证据",
    tooltip: "该结论有论文原文直接支持",
    color: "var(--color-evidence-a)",
    bgColor: "var(--color-evidence-a-bg)",
  },
  {
    label: "B",
    title: "综合归纳",
    tooltip: "该结论通过多篇论文综合归纳得出",
    color: "var(--color-evidence-b)",
    bgColor: "var(--color-evidence-b-bg)",
  },
  {
    label: "C",
    title: "迁移推断",
    tooltip: "该结论是跨领域逻辑迁移推断",
    color: "var(--color-evidence-c)",
    bgColor: "var(--color-evidence-c-bg)",
  },
];

/* ================================================================== */
/*  Sub-components                                                     */
/* ================================================================== */

function AcademicIllustration() {
  return (
    <svg
      viewBox="0 0 200 200"
      className="w-[180px] h-[180px] sm:w-[200px] sm:h-[200px]"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="hero-glow" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stopColor="#C9A84C" stopOpacity="0.18" />
          <stop offset="100%" stopColor="#C9A84C" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="hero-c1" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stopColor="#C9A84C" stopOpacity="0.15" />
          <stop offset="100%" stopColor="#C9A84C" stopOpacity="0.04" />
        </radialGradient>
        <radialGradient id="hero-c2" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stopColor="#8E8E9A" stopOpacity="0.12" />
          <stop offset="100%" stopColor="#8E8E9A" stopOpacity="0.03" />
        </radialGradient>
        <linearGradient id="hero-book" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#C9A84C" stopOpacity="0.1" />
          <stop offset="100%" stopColor="#C9A84C" stopOpacity="0.02" />
        </linearGradient>
      </defs>

      {/* Background glow */}
      <circle cx="100" cy="100" r="88" fill="url(#hero-glow)" />

      {/* Light rays radiating from center */}
      <g opacity="0.12" stroke="#C9A84C" strokeWidth="0.6" strokeLinecap="round">
        <line x1="100" y1="100" x2="18" y2="18" />
        <line x1="100" y1="100" x2="182" y2="28" />
        <line x1="100" y1="100" x2="12" y2="135" />
        <line x1="100" y1="100" x2="188" y2="165" />
        <line x1="100" y1="100" x2="100" y2="8" />
        <line x1="100" y1="100" x2="100" y2="192" />
        <line x1="100" y1="100" x2="40" y2="175" />
        <line x1="100" y1="100" x2="160" y2="175" />
      </g>

      {/* Outer ring */}
      <circle
        cx="100"
        cy="100"
        r="72"
        stroke="#C9A84C"
        strokeWidth="0.5"
        fill="none"
        opacity="0.12"
      />

      {/* Overlapping circles — knowledge nodes */}
      <circle cx="68" cy="72" r="30" stroke="#C9A84C" strokeWidth="1" fill="url(#hero-c1)" opacity="0.65" />
      <circle cx="132" cy="74" r="24" stroke="#C9A84C" strokeWidth="0.9" fill="url(#hero-c1)" opacity="0.5" />
      <circle cx="82" cy="128" r="22" stroke="#8E8E9A" strokeWidth="0.8" fill="url(#hero-c2)" opacity="0.45" />
      <circle cx="128" cy="118" r="20" stroke="#8E8E9A" strokeWidth="0.7" fill="url(#hero-c2)" opacity="0.4" />

      {/* Central book / document */}
      <g transform="translate(100, 92)">
        <rect
          x="-22"
          y="-14"
          width="44"
          height="30"
          rx="3"
          stroke="#C9A84C"
          strokeWidth="1.2"
          fill="url(#hero-book)"
        />
        {/* Book spine */}
        <line x1="0" y1="-14" x2="0" y2="16" stroke="#C9A84C" strokeWidth="0.8" opacity="0.4" />
        {/* Text lines */}
        <line x1="-14" y1="-5" x2="-4" y2="-5" stroke="#C9A84C" strokeWidth="0.6" opacity="0.5" />
        <line x1="5" y1="-5" x2="14" y2="-5" stroke="#C9A84C" strokeWidth="0.6" opacity="0.5" />
        <line x1="-14" y1="0" x2="14" y2="0" stroke="#C9A84C" strokeWidth="0.6" opacity="0.5" />
        <line x1="-10" y1="5" x2="10" y2="5" stroke="#C9A84C" strokeWidth="0.6" opacity="0.35" />
      </g>

      {/* Small decorative dots */}
      <circle cx="36" cy="48" r="2.5" fill="#C9A84C" opacity="0.25" />
      <circle cx="165" cy="48" r="2" fill="#C9A84C" opacity="0.2" />
      <circle cx="55" cy="158" r="2" fill="#8E8E9A" opacity="0.2" />
      <circle cx="155" cy="155" r="2.5" fill="#C9A84C" opacity="0.25" />
      <circle cx="32" cy="105" r="1.8" fill="#8E8E9A" opacity="0.18" />
      <circle cx="170" cy="108" r="1.5" fill="#C9A84C" opacity="0.15" />
    </svg>
  );
}

function TypewriterTitle({
  text,
  displayText,
  showCursor,
}: {
  text: string;
  displayText: string;
  showCursor: boolean;
}) {
  return (
    <h1 className="text-2xl sm:text-3xl font-serif font-semibold text-[var(--text-primary)]">
      <span>{displayText}</span>
      {showCursor && displayText === text && (
        <span className="inline-block ml-0.5 w-[2px] h-[1.1em] bg-[var(--color-gold)] align-middle animate-pulse-subtle" />
      )}
      {showCursor && displayText !== text && (
        <span className="inline-block ml-0.5 w-[2px] h-[1.1em] bg-[var(--color-gold)] align-middle animate-pulse-subtle" />
      )}
    </h1>
  );
}

/* ================================================================== */
/*  Stats bar sub-component                                            */
/* ================================================================== */

function StatsBar({ prefersReducedMotion }: { prefersReducedMotion: boolean }) {
  return (
    <div className="flex items-center justify-center gap-4 sm:gap-6 flex-wrap">
      {STATS.map((stat, i) => {
        const delay = prefersReducedMotion ? 0 : i * 0.15;
        return (
          <motion.div
            key={stat.label}
            initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              delay,
              duration: 0.5,
              ease: "easeOut",
            }}
            className="flex items-center gap-1.5 text-[0.7rem] text-[var(--text-tertiary)]"
          >
            <span className="text-[0.8rem]">{stat.icon}</span>
            <span>
              <span className="text-[var(--text-secondary)] font-medium">{stat.value}</span>
              <span className="ml-0.5">{stat.label}</span>
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}

/* ================================================================== */
/*  Main component                                                    */
/* ================================================================== */

export function ChatContainer() {
  /* ── Store ── */
  const {
    messages,
    isStreaming,
    addMessage,
    appendToLastMessage,
    setLastMessageEvidence,
    setStreaming,
  } = useChatStore();

  /* ── Refs ── */
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  /* ── UI state ── */
  const [showEmpty, setShowEmpty] = useState(true);

  /* ── Loading phase (from SSE status events) ── */
  const [loadingPhase, setLoadingPhase] = useState<
    "retrieving" | "found" | "generating" | null
  >(null);
  const [sectionsCount, setSectionsCount] = useState<number | null>(null);

  /* ── First-message celebration state ── */
  const [isFirstAnswer, setIsFirstAnswer] = useState(false);
  const [shimmerSweep, setShimmerSweep] = useState(false);

  /* ── Typewriter state ── */
  const [displayedTitle, setDisplayedTitle] = useState("");
  const [showCursor, setShowCursor] = useState(true);
  const [typingComplete, setTypingComplete] = useState(false);
  const subtitleControls = useAnimation();
  const prefersReducedMotion = useReducedMotion();

  /* ── Auto-scroll to bottom ── */
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  /* ── VisualViewport API handler for mobile keyboard ── */
  useEffect(() => {
    if (typeof window === "undefined") return;
    const vv = window.visualViewport;
    if (!vv) return;

    const handleResize = () => {
      // On iOS, when the keyboard opens, the visual viewport shrinks.
      // We set a CSS custom property so the sticky input bar adjusts.
      document.documentElement.style.setProperty(
        "--visual-viewport-height",
        `${vv.height}px`
      );
    };

    vv.addEventListener("resize", handleResize);
    handleResize();
    return () => vv.removeEventListener("resize", handleResize);
  }, []);

  /* ── Typewriter effect ── */
  useEffect(() => {
    if (!showEmpty) {
      setDisplayedTitle("");
      setTypingComplete(false);
      return;
    }

    setDisplayedTitle("");
    setShowCursor(true);
    setTypingComplete(false);

    if (prefersReducedMotion) {
      setDisplayedTitle(TITLE);
      setTypingComplete(true);
      setShowCursor(false);
      subtitleControls.set({ opacity: 1, y: 0 });
      return;
    }

    let mounted = true;
    let charIndex = 0;

    const typeNext = () => {
      if (!mounted) return;
      if (charIndex < TITLE.length) {
        charIndex++;
        setDisplayedTitle(TITLE.slice(0, charIndex));
        setTimeout(typeNext, 50);
      } else {
        setTypingComplete(true);
        // Fade in subtitle
        subtitleControls.start({
          opacity: 1,
          y: 0,
          transition: { duration: 0.6, ease: "easeOut" },
        });
        // Fade cursor after 2s
        setTimeout(() => {
          if (mounted) setShowCursor(false);
        }, 2000);
      }
    };

    const initialTimer = setTimeout(typeNext, 400);

    return () => {
      mounted = false;
      clearTimeout(initialTimer);
    };
  }, [showEmpty, prefersReducedMotion, subtitleControls]);

  /* ── Handle send ── */
  const handleSend = useCallback(
    async (content: string) => {
      if (isStreaming) return;

      setShowEmpty(false);
      setLoadingPhase("retrieving");
      setSectionsCount(null);

      // ── First-message celebration check ──
      const isFirst = !hasAskedBefore();
      if (isFirst) {
        markAsked();
        setIsFirstAnswer(true);
        // Trigger shimmer sweep on input area
        setShimmerSweep(true);
        setTimeout(() => setShimmerSweep(false), 1500);
      } else {
        setIsFirstAnswer(false);
      }

      // Add user message
      const userMsg: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content,
        timestamp: Date.now(),
      };
      addMessage(userMsg);

      // Add placeholder assistant message
      const assistantId = `assistant-${Date.now()}`;
      const assistantMsg: Message = {
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: Date.now(),
      };
      addMessage(assistantMsg);
      setStreaming(true);

      // Parse SSE stream from API
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question: content,
            api_key: (() => { try { return localStorage.getItem("deepseek_api_key") || ""; } catch { return ""; } })(),
            session_id: `web-${Date.now()}`,
          }),
          signal: abortRef.current?.signal,
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("No response body");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const data = line.slice(6).trim();
            if (!data) continue;

            try {
              const parsed = JSON.parse(data);

              // Handle SSE event types from the backend
              if (parsed.chunk) {
                // answer event — append streaming text
                appendToLastMessage(parsed.chunk);
              } else if (parsed.phase === "context-assembly") {
                // Status update — track loading phase
                setLoadingPhase("retrieving");
                if (parsed.sections_count != null) {
                  setSectionsCount(parsed.sections_count);
                  setLoadingPhase("found");
                }
              } else if (parsed.phase === "answer") {
                // Answer phase started
                setLoadingPhase("generating");
              } else if (parsed.session_id) {
                // Done event — capture session
              }
            } catch {
              // If not JSON, treat as raw text chunk
              if (data && data !== "[DONE]") {
                appendToLastMessage(data);
              }
            }
          }
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name !== "AbortError") {
          appendToLastMessage(
            `\n\n*连接中断，请重试。错误：${err.message}*`
          );
        }
      } finally {
        setStreaming(false);
        setLoadingPhase(null);
      }
    },
    [
      isStreaming,
      addMessage,
      appendToLastMessage,
      setLastMessageEvidence,
      setStreaming,
    ]
  );

  /* ── Render ── */
  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-6 scroll-smooth overscroll-contain"
      >
        <AnimatePresence mode="wait">
          {showEmpty && messages.length === 0 ? (
            /* ════════════════ WELCOME / EMPTY STATE ════════════════ */
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
              className="h-full flex flex-col items-center justify-center min-h-[60vh]"
            >
              {/* ── Hero illustration ── */}
              <motion.div
                initial={{ opacity: 0, scale: 0.92 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.7, ease: "easeOut" }}
                className="mb-8"
              >
                <AcademicIllustration />
              </motion.div>

              {/* ── Typewriter title ── */}
              <div className="mb-2 h-9">
                <TypewriterTitle
                  text={TITLE}
                  displayText={displayedTitle}
                  showCursor={showCursor}
                />
              </div>

              {/* ── Subtitle ── */}
              <motion.p
                initial={prefersReducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
                animate={subtitleControls}
                className="text-sm text-[var(--text-secondary)] mb-6 max-w-md text-center leading-relaxed"
              >
                基于陈志远教授 15 篇公开论文炼化出的 AI 科研助手。
                <br />
                通信安全、IIoT安全、UAV安全通信、可信计算、隐私保护。
              </motion.p>

              {/* ── Stats bar ── */}
              <div className="mb-10">
                <StatsBar prefersReducedMotion={!!prefersReducedMotion} />
              </div>

              {/* ── Example question cards ── */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-xl w-full">
                {EXAMPLE_QUESTIONS.map((q) => {
                  const Icon = q.icon;
                  return (
                    <button
                      key={q.label}
                      onClick={() => handleSend(q.question)}
                      disabled={isStreaming}
                      className="group text-left p-4 sm:p-5 card-surface hover:border-[var(--color-gold)]/40 hover:bg-[var(--bg-hover)] hover:-translate-y-1 active:translate-y-0 transition-all duration-200"
                    >
                      <div className="flex items-start gap-3 sm:gap-4">
                        {/* Icon */}
                        <div className="flex-shrink-0 w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-[var(--color-gold)]/8 border border-[var(--color-gold)]/15 flex items-center justify-center group-hover:bg-[var(--color-gold)]/15 group-hover:border-[var(--color-gold)]/25 transition-colors duration-200">
                          <Icon
                            size={16}
                            className="text-[var(--color-gold)]"
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          {/* Label */}
                          <span className="text-[0.6rem] sm:text-[0.65rem] font-semibold uppercase tracking-wider text-[var(--color-gold)] block mb-0.5">
                            {q.label}
                          </span>
                          {/* Question */}
                          <span className="text-xs sm:text-sm text-[var(--text-secondary)] group-hover:text-[var(--text-primary)] transition-colors leading-relaxed block">
                            {q.question}
                          </span>
                          {/* Description */}
                          <span className="text-[0.6rem] sm:text-[0.65rem] text-[var(--text-tertiary)] mt-1 block group-hover:text-[var(--text-secondary)]/80 transition-colors">
                            {q.description}
                          </span>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* ── Evidence legend pill badges ── */}
              <div className="mt-10 flex items-center gap-2 flex-wrap justify-center">
                {EVIDENCE_ITEMS.map((item) => (
                  <Tooltip.Root key={item.label}>
                    <Tooltip.Trigger asChild>
                      <button
                        type="button"
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[0.6rem] font-semibold font-mono tracking-wide border transition-all duration-200 cursor-default"
                        style={{
                          color: item.color,
                          backgroundColor: item.bgColor,
                          borderColor: `${item.color}35`,
                        }}
                      >
                        {item.label} {item.title}
                      </button>
                    </Tooltip.Trigger>
                    <Tooltip.Portal>
                      <Tooltip.Content
                        side="top"
                        sideOffset={6}
                        className="z-50 max-w-[200px]"
                      >
                        {item.tooltip}
                        <Tooltip.Arrow
                          className="fill-[var(--bg-elevated)]"
                          width={10}
                          height={5}
                        />
                      </Tooltip.Content>
                    </Tooltip.Portal>
                  </Tooltip.Root>
                ))}
              </div>
            </motion.div>
          ) : (
            /* ════════════════ MESSAGES VIEW ════════════════ */
            <motion.div
              key="messages"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="max-w-3xl 2xl:max-w-[900px] mx-auto space-y-6 pb-4"
            >
              {messages.map((msg) => (
                <MessageBubble
                  key={msg.id}
                  message={msg}
                  isStreaming={
                    isStreaming &&
                    msg.id === messages[messages.length - 1]?.id &&
                    msg.role === "assistant"
                  }
                  isFirstAnswer={
                    isFirstAnswer &&
                    msg.role === "assistant" &&
                    msg.id === messages.find((m) => m.role === "assistant")?.id
                  }
                />
              ))}

              {/* ── Skeleton while waiting for answer ── */}
              {isStreaming &&
                messages.length > 0 &&
                !messages[messages.length - 1].content && (
                  <div className="flex gap-3 sm:gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--color-gold)]/15 border border-[var(--color-gold)]/20 flex items-center justify-center">
                      <span className="text-[0.7rem] font-semibold font-mono text-[var(--color-gold)]">
                        S
                      </span>
                    </div>
                    <div className="flex-1 max-w-[90%] sm:max-w-[80%] lg:max-w-[75%]">
                      <AnswerSkeleton
                        loadingPhase={loadingPhase}
                        sectionsCount={sectionsCount}
                      />
                    </div>
                  </div>
                )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Input bar — sticky bottom with safe area support */}
      <div className={`flex-shrink-0 sticky bottom-0 z-10 px-4 sm:px-6 lg:px-8 pt-4 safe-bottom border-t border-[var(--border-subtle)] bg-[var(--bg-base)]/80 backdrop-blur-xl ${shimmerSweep ? "shimmer-sweep" : ""}`}>
        <div className="max-w-3xl 2xl:max-w-[900px] mx-auto">
          <InputBar onSend={handleSend} disabled={isStreaming} isFirstMessage={isFirstAnswer} />
        </div>
      </div>
    </div>
  );
}
