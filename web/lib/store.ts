"use client";

import { create } from "zustand";

export type EvidenceLevel = "A" | "B" | "C";

export interface EvidenceSection {
  level: EvidenceLevel;
  title: string;
  content: string;
  papers: string[];
}

export interface SourcePaper {
  id: string;
  title: string;
  url?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  evidenceSections?: EvidenceSection[];
  sourcePapers?: SourcePaper[];
}

export interface ChatSession {
  id: string;
  title: string;
  timestamp: number;
  messageCount: number;
}

interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  sessionId: string | null;
  sessions: ChatSession[];
  sidebarOpen: boolean;
  addMessage: (msg: Message) => void;
  updateLastMessage: (content: string) => void;
  appendToLastMessage: (chunk: string) => void;
  setLastMessageEvidence: (sections: EvidenceSection[], papers: SourcePaper[]) => void;
  setStreaming: (v: boolean) => void;
  clearMessages: () => void;
  setSessionId: (id: string) => void;
  setSessions: (sessions: ChatSession[]) => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  sessionId: null,
  sidebarOpen: false,
  sessions: [
    {
      id: "1",
      title: "图像复原方法概述",
      timestamp: Date.now() - 3600000,
      messageCount: 8,
    },
    {
      id: "2",
      title: "计算成像与感知",
      timestamp: Date.now() - 86400000,
      messageCount: 12,
    },
    {
      id: "3",
      title: "联邦学习研究路径",
      timestamp: Date.now() - 172800000,
      messageCount: 5,
    },
  ],

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, msg],
    })),

  updateLastMessage: (content) =>
    set((state) => {
      const msgs = [...state.messages];
      const last = msgs[msgs.length - 1];
      if (last && last.role === "assistant") {
        msgs[msgs.length - 1] = { ...last, content };
      }
      return { messages: msgs };
    }),

  appendToLastMessage: (chunk) =>
    set((state) => {
      const msgs = [...state.messages];
      const last = msgs[msgs.length - 1];
      if (last && last.role === "assistant") {
        msgs[msgs.length - 1] = { ...last, content: last.content + chunk };
      }
      return { messages: msgs };
    }),

  setLastMessageEvidence: (sections, papers) =>
    set((state) => {
      const msgs = [...state.messages];
      const last = msgs[msgs.length - 1];
      if (last && last.role === "assistant") {
        msgs[msgs.length - 1] = { ...last, evidenceSections: sections, sourcePapers: papers };
      }
      return { messages: msgs };
    }),

  setStreaming: (v) => set({ isStreaming: v }),

  clearMessages: () => set({ messages: [], sessionId: null }),

  setSessionId: (id) => set({ sessionId: id }),

  setSessions: (sessions) => set({ sessions }),

  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
