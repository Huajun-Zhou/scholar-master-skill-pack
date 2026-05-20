"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useReducedMotion } from "framer-motion";

/* ------------------------------------------------------------------ */
/*  Content widths for staggered skeleton bars                        */
/* ------------------------------------------------------------------ */
const TITLE_WIDTH = "60%";
const CONTENT_WIDTHS = ["90%", "75%", "85%", "60%"];
const EVIDENCE_TINTS = [
  { level: "A", color: "var(--color-evidence-a)", bg: "rgba(212,168,75,0.08)", width: "42%" },
  { level: "B", color: "var(--color-evidence-b)", bg: "rgba(142,142,154,0.08)", width: "38%" },
  { level: "C", color: "var(--color-evidence-c)", bg: "rgba(160,105,75,0.06)", width: "35%" },
];

/* ------------------------------------------------------------------ */
/*  Framer-motion variants for staggered entrance                     */
/* ------------------------------------------------------------------ */
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const barVariants = {
  hidden: { opacity: 0, y: 8 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: "easeOut" as const },
  },
};

/* ------------------------------------------------------------------ */
/*  Phase icons                                                       */
/* ------------------------------------------------------------------ */

const PHASE_ICONS: Record<string, { icon: string; label: string }> = {
  retrieving: { icon: "🔍", label: "正在检索相关知识..." },
  found: { icon: "✓", label: "已找到方法卡" },
  generating: { icon: "✨", label: "正在生成回答..." },
};

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */
interface AnswerSkeletonProps {
  loadingPhase?: "retrieving" | "found" | "generating" | null;
  sectionsCount?: number | null;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */
export function AnswerSkeleton({ loadingPhase, sectionsCount }: AnswerSkeletonProps) {
  const prefersReducedMotion = useReducedMotion();

  const phaseInfo = loadingPhase ? PHASE_ICONS[loadingPhase] : null;
  const foundLabel =
    loadingPhase === "found" && sectionsCount != null
      ? `已找到 ${sectionsCount} 个方法卡，正在分析...`
      : phaseInfo?.label;

  return (
    <motion.div
      className="flex flex-col gap-4 py-2"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* ── Phase indicator with animated icon + crossfade text ── */}
      {loadingPhase && (
        <motion.div
          variants={barVariants}
          className="flex items-center gap-2 mb-1"
        >
          <AnimatePresence mode="wait">
            <motion.span
              key={loadingPhase}
              initial={prefersReducedMotion ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.6 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.6 }}
              transition={{ duration: 0.25 }}
              className="text-sm"
            >
              {phaseInfo?.icon}
            </motion.span>
          </AnimatePresence>
          <AnimatePresence mode="wait">
            <motion.span
              key={foundLabel}
              initial={prefersReducedMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 8 }}
              transition={{ duration: 0.25 }}
              className="text-[0.65rem] font-mono text-[var(--color-gold)]/70 tracking-wide"
            >
              {foundLabel}
            </motion.span>
          </AnimatePresence>
          {loadingPhase === "retrieving" && (
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-gold)] animate-pulse-subtle" />
          )}
        </motion.div>
      )}

      {/* ── Title bar – gold-tinted, wide ── */}
      <motion.div
        variants={barVariants}
        className="h-4 rounded shimmer-bar bg-[var(--color-gold)]/12"
        style={{ width: TITLE_WIDTH }}
      />

      {/* ── Content lines – staggered widths ── */}
      <div className="space-y-2.5 mt-1">
        {CONTENT_WIDTHS.map((width, i) => (
          <motion.div
            key={`c-${i}`}
            variants={barVariants}
            className="h-2.5 rounded shimmer-bar bg-[var(--bg-elevated)]"
            style={{ width }}
          />
        ))}
      </div>

      {/* ── Evidence section placeholders – gold/silver/bronze ── */}
      <div className="space-y-3 mt-3">
        {EVIDENCE_TINTS.map((tint, i) => (
          <motion.div
            key={`ev-${tint.level}`}
            variants={barVariants}
            className="flex items-center gap-3"
          >
            {/* Level badge */}
            <span
              className="inline-flex items-center justify-center w-5 h-5 rounded-full text-[0.55rem] font-bold font-mono flex-shrink-0"
              style={{
                backgroundColor: tint.color + "18",
                color: tint.color,
                border: `1px solid ${tint.color}25`,
              }}
            >
              {tint.level}
            </span>
            {/* Tinted shimmer bar */}
            <div
              className="h-3 rounded shimmer-bar"
              style={{ width: tint.width, background: tint.bg }}
            />
          </motion.div>
        ))}
      </div>

      {/* ── Source-paper chip placeholder ── */}
      <motion.div
        variants={barVariants}
        className="h-3 rounded-full shimmer-bar bg-[var(--bg-elevated)] mt-1"
        style={{ width: "28%" }}
      />
    </motion.div>
  );
}
