"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";
import { EvidenceBadge } from "@/components/evidence/EvidenceBadge";

const EVIDENCE_PATTERN = /\[EVID-([A-Z]+)-([A-Za-z0-9_]+)-([A-Z])-([a-z0-9]+)\]/g;

function parseEvidenceTags(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  const pattern = /\[EVID-([A-Z]+)-([A-Za-z0-9_]+)-([A-Z])-([a-z0-9]+)\]/g;
  while ((match = pattern.exec(text)) !== null) {
    // Text before this match
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    const [, paperId, category, level, evidenceId] = match;
    parts.push(
      <EvidenceBadge
        key={match.index}
        level={level as "A" | "B" | "C"}
        evidenceId={evidenceId}
        paperTitle={paperId.replace(/_/g, " ")}
      />
    );

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : [text];
}

function transformTextWithEvidence(node: React.ReactNode): React.ReactNode {
  if (typeof node === "string") {
    const parsed = parseEvidenceTags(node);
    if (parsed.length === 1 && parsed[0] === node) return node;
    return React.createElement(React.Fragment, null, ...parsed);
  }
  return node;
}

export function MarkdownRenderer({ content }: { content: string }) {
  const components: Partial<Components> = {
    a: ({ href, children, ...props }) => {
      const isInternal =
        href?.startsWith("/") || href?.startsWith("#");
      const isWiki =
        href?.startsWith("/wiki/") || href?.startsWith("/papers/");

      if (isWiki) {
        return (
          <a
            href={href}
            className="text-[var(--color-gold)] hover:text-[var(--color-gold-bright)] underline underline-offset-2 decoration-[var(--color-gold-dim)]/30 transition-colors"
            {...props}
          >
            {children}
          </a>
        );
      }

      if (isInternal) {
        return (
          <a
            href={href}
            className="text-[var(--color-gold)] hover:text-[var(--color-gold-bright)] transition-colors"
            {...props}
          >
            {children}
          </a>
        );
      }

      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[var(--color-gold)] hover:text-[var(--color-gold-bright)] underline underline-offset-2 decoration-[var(--color-gold-dim)]/30 transition-colors"
          {...props}
        >
          {children}
          <svg
            className="inline-block w-3 h-3 ml-0.5 opacity-60"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
        </a>
      );
    },

    code: ({ className, children, ...props }) => {
      const isInline = !className;
      if (isInline) {
        return (
          <code
            className="text-[var(--color-gold-dim)] bg-[var(--bg-elevated)] px-1.5 py-0.5 rounded text-[0.8em] font-mono border border-[var(--border-default)]"
            {...props}
          >
            {children}
          </code>
        );
      }

      return (
        <div className="relative group my-4">
          <button
            onClick={() => {
              navigator.clipboard.writeText(String(children).replace(/\n$/, ""));
            }}
            className="absolute top-2 right-2 px-2 py-1 text-[0.7rem] font-mono text-[var(--text-tertiary)] bg-[var(--bg-surface)] border border-[var(--border-default)] rounded opacity-0 group-hover:opacity-100 transition-opacity hover:text-[var(--color-gold)] hover:border-[var(--border-accent)]"
          >
            复制
          </button>
          <pre className="bg-[var(--bg-elevated)] border border-[var(--border-default)] rounded-lg p-4 overflow-x-auto stream-code-block">
            <code className="text-sm font-mono text-[var(--text-primary)]" {...props}>
              {children}
            </code>
          </pre>
        </div>
      );
    },

    table: ({ children }) => (
      <div className="overflow-x-auto my-4">
        <table className="w-full border-collapse text-sm">
          {children}
        </table>
      </div>
    ),

    th: ({ children }) => (
      <th className="px-3 py-2 text-left text-[0.75rem] font-semibold uppercase tracking-wider text-[var(--text-secondary)] border-b border-[var(--border-subtle)]">
        {children}
      </th>
    ),

    td: ({ children }) => (
      <td className="px-3 py-2 text-[var(--text-primary)] border-b border-[var(--border-subtle)]">
        {children}
      </td>
    ),

    blockquote: ({ children }) => (
      <blockquote className="border-l-[3px] border-[var(--color-gold)] pl-5 my-4 text-[var(--text-secondary)] italic">
        {children}
      </blockquote>
    ),

    h1: ({ children }) => (
      <h1 className="text-xl font-serif font-semibold text-[var(--text-primary)] mt-8 mb-3 tracking-tight leading-snug">
        {children}
      </h1>
    ),

    h2: ({ children }) => (
      <h2 className="text-lg font-serif font-semibold text-[var(--text-primary)] mt-6 mb-2 tracking-tight border-b border-[var(--border-subtle)] pb-1 leading-snug stream-header">
        {children}
      </h2>
    ),

    h3: ({ children }) => (
      <h3 className="text-base font-serif font-semibold text-[var(--text-secondary)] mt-4 mb-2 leading-snug stream-header">
        {children}
      </h3>
    ),

    p: ({ children }) => {
      const processed = React.Children.map(children, transformTextWithEvidence);
      return <p className="my-4 leading-relaxed stream-paragraph">{processed}</p>;
    },

    li: ({ children }) => {
      const processed = React.Children.map(children, transformTextWithEvidence);
      return <li className="my-1.5 leading-relaxed">{processed}</li>;
    },

    hr: () => (
      <hr className="border-t border-[var(--border-subtle)] my-6" />
    ),

    strong: ({ children }) => (
      <strong className="font-semibold text-[var(--text-primary)]">{children}</strong>
    ),
  };

  return (
    <div className="prose-wiki">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
