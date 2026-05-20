"use client";

import { Navigation } from "@/components/common/Navigation";
import { Sidebar } from "@/components/common/Sidebar";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { useChatStore } from "@/lib/store";

export default function ChatPage() {
  const sidebarOpen = useChatStore((s) => s.sidebarOpen);

  return (
    <div className="flex flex-col h-dvh bg-[var(--bg-base)] overflow-hidden">
      <Navigation />
      <div className="flex flex-1 pt-14 overflow-hidden overscroll-none">
        {/* Sidebar — handles responsive behavior internally */}
        <Sidebar />
        {/* Main content — margin adjusts based on sidebar state */}
        <main
          className={[
            "flex-1 flex flex-col min-w-0",
            "transition-all duration-300 ease-in-out",
            sidebarOpen ? "md:ml-[240px]" : "",
            "lg:ml-[320px]",
          ]
            .filter(Boolean)
            .join(" ")}
        >
          <ChatContainer />
        </main>
      </div>
      {/* Cinema mode decorative gradients (> 1440px) */}
      <div
        className="hidden min-[1440px]:block fixed inset-0 pointer-events-none z-0"
        aria-hidden="true"
      >
        <div
          className="cinema-decoration cinema-left"
          style={{ width: `calc((100vw - 1440px) / 2)` }}
        />
        <div
          className="cinema-decoration cinema-right"
          style={{ width: `calc((100vw - 1440px) / 2)` }}
        />
      </div>
    </div>
  );
}
