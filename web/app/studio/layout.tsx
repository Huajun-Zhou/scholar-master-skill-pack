"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/studio/design", label: "学者委员会", icon: "⚖" },
  { href: "/studio/ask", label: "学者问答", icon: "?" },
  { href: "/studio/critique", label: "论文审查", icon: "◇" },
  { href: "/reports", label: "运行历史", icon: "☰" },
  { href: "/compare", label: "方案对比", icon: "⇔" },
];

export default function StudioLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-full">
      {/* 左侧导航 */}
      <nav className="w-48 shrink-0 border-r border-zinc-800 p-3 flex flex-col gap-1">
        <Link
          href="/studio"
          className="text-zinc-400 text-xs font-medium uppercase tracking-wider px-2 mb-2"
        >
          研究工作室
        </Link>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm transition-colors
                ${isActive
                  ? "bg-amber-500/10 text-amber-400"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
                }`}
            >
              <span className="text-xs w-4 text-center">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* 主内容 */}
      <main className="flex-1 min-w-0 p-6 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
