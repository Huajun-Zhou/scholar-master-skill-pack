"use client";

import { create } from "zustand";

export type WorkflowType = "ask" | "design" | "critique" | "committee";

export interface AgentMessage {
  agent: string;
  content: string;
  timestamp: string;
  toolCalls?: string[];
}

export interface WorkflowRun {
  runId: string;
  workflow: WorkflowType;
  status: "idle" | "running" | "completed" | "error";
  agentMessages: AgentMessage[];
  gateResult?: { passed: boolean; summary: string };
  error?: string;
}

interface StudioState {
  activeRun: WorkflowRun | null;
  runHistory: WorkflowRun[];
  setActiveRun: (run: WorkflowRun | null) => void;
  addAgentMessage: (runId: string, msg: AgentMessage) => void;
  setGateResult: (runId: string, result: { passed: boolean; summary: string }) => void;
  setRunStatus: (runId: string, status: WorkflowRun["status"], error?: string) => void;
  clearRun: (runId: string) => void;
}

export const useStudioStore = create<StudioState>((set) => ({
  activeRun: null,
  runHistory: [],

  setActiveRun: (run) => set({ activeRun: run }),

  addAgentMessage: (runId, msg) =>
    set((state) => {
      const updateRun = (r: WorkflowRun) =>
        r.runId === runId
          ? { ...r, agentMessages: [...r.agentMessages, msg] }
          : r;
      return {
        activeRun: state.activeRun ? updateRun(state.activeRun) : null,
        runHistory: state.runHistory.map(updateRun),
      };
    }),

  setGateResult: (runId, result) =>
    set((state) => {
      const updateRun = (r: WorkflowRun) =>
        r.runId === runId ? { ...r, gateResult: result } : r;
      return {
        activeRun: state.activeRun ? updateRun(state.activeRun) : null,
        runHistory: state.runHistory.map(updateRun),
      };
    }),

  setRunStatus: (runId, status, error) =>
    set((state) => {
      const updateRun = (r: WorkflowRun) =>
        r.runId === runId ? { ...r, status, error } : r;
      return {
        activeRun: state.activeRun ? updateRun(state.activeRun) : null,
        runHistory: state.runHistory.map(updateRun),
      };
    }),

  clearRun: (runId) =>
    set((state) => ({
      runHistory: state.runHistory.filter((r) => r.runId !== runId),
      activeRun: state.activeRun?.runId === runId ? null : state.activeRun,
    })),
}));
