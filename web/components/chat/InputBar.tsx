"use client";

import { useState, useRef, useEffect, useCallback, type KeyboardEvent } from "react";
import { motion } from "framer-motion";

interface InputBarProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  isFirstMessage?: boolean;
}

export function InputBar({
  onSend,
  disabled = false,
  placeholder = "向 Scholar 提问…",
  isFirstMessage = false,
}: InputBarProps) {
  const [value, setValue] = useState("");
  const [showRipple, setShowRipple] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 200) + "px";
    }
  }, [value]);

  // Focus on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    // Reset height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleRipple = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      if (disabled || !value.trim()) return;
      // Trigger ripple effect via CSS
      const btn = buttonRef.current;
      if (btn) {
        const rect = btn.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        btn.style.setProperty("--ripple-x", `${x}%`);
        btn.style.setProperty("--ripple-y", `${y}%`);
      }
      setShowRipple(true);
      setTimeout(() => setShowRipple(false), 600);
      handleSend();
    },
    [disabled, value, handleSend]
  );

  const hasText = value.trim().length > 0;
  const charCount = value.length;

  return (
    <div className="relative">
      <div
        className={`
          relative flex items-end gap-2 sm:gap-2.5
          bg-[var(--bg-surface)]
          rounded-xl px-3 sm:px-4 py-2.5 sm:py-3
          transition-all duration-200
          focus-within:border-[var(--color-gold)]/40
          ${
            hasText
              ? "border border-[var(--color-gold)]/40 shadow-[0_0_20px_rgba(201,168,76,0.08)]"
              : "border border-[var(--border-default)]"
          }
          focus-within:shadow-[0_0_0_2px_rgba(201,168,76,0.3)]
        `}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="flex-1 bg-transparent text-[var(--text-primary)] placeholder-[var(--text-tertiary)] resize-none outline-none text-sm sm:text-base leading-relaxed max-h-[200px] font-sans"
        />

        <motion.button
          ref={buttonRef}
          onClick={handleRipple}
          disabled={disabled || !hasText}
          initial={{ scale: 1 }}
          animate={
            hasText
              ? isFirstMessage
                ? { scale: [0.9, 1] }
                : { scale: [0.97, 1] }
              : { scale: 1 }
          }
          transition={
            hasText
              ? { type: "spring", stiffness: 300, damping: 20 }
              : {}
          }
          className={`
            flex-shrink-0 flex items-center justify-center
            w-12 h-12 sm:w-9 sm:h-9
            min-w-[48px] min-h-[48px] sm:min-w-0 sm:min-h-0
            rounded-lg
            transition-all duration-200 relative overflow-hidden
            ${
              disabled || !hasText
                ? "bg-[var(--bg-elevated)] text-[var(--text-tertiary)] cursor-not-allowed"
                : "bg-[var(--color-gold)] text-[#0A0A0F] hover:shadow-[0_0_16px_rgba(201,168,76,0.3)] cursor-pointer"
            }
          `}
          aria-label="发送"
        >
          {showRipple && hasText && (
            <span
              className="absolute inset-0 pointer-events-none rounded-lg"
              style={{
                background:
                  "radial-gradient(circle at var(--ripple-x, 50%) var(--ripple-y, 50%), rgba(255,255,255,0.4) 0%, transparent 60%)",
                animation: "ripple 0.6s ease-out forwards",
              }}
            />
          )}
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="relative z-10"
          >
            <path d="M22 2L11 13" />
            <path d="M22 2L15 22L11 13L2 9L22 2Z" />
          </svg>
        </motion.button>
      </div>

      <div className="flex items-center justify-between mt-1.5 px-2">
        {/* Character counter — shown when > 500 chars */}
        {charCount > 500 && (
          <span
            className={`text-[0.6rem] transition-colors duration-200 ${
              charCount > 2000
                ? "text-[var(--color-red)]"
                : charCount > 1000
                  ? "text-[var(--color-amber)]"
                  : "text-[var(--text-tertiary)]"
            }`}
          >
            {charCount}
          </span>
        )}
        {charCount <= 500 && <span />}

        <p className="text-[0.6rem] sm:text-[0.65rem] text-[var(--text-tertiary)] text-center">
          Enter 发送 · Shift+Enter 换行 · Scholar 回答基于 A/B/C 三级证据体系
        </p>
      </div>
    </div>
  );
}
