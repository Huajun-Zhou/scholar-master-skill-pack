import type { Metadata } from "next";
import { Inter, IBM_Plex_Serif, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import * as Tooltip from "@radix-ui/react-tooltip";
import { SearchDialog } from "@/components/common/SearchDialog";
import { ScrollToTop } from "@/components/common/ScrollToTop";

// next/font/google automatically:
//  - Generates <link rel="preload"> for the selected weights (bold IBM Plex Serif for headings)
//  - Handles subsetting to latin for efficient loading
//  - Injects CSS custom properties for the font family
const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const ibmPlexSerif = IBM_Plex_Serif({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-serif",
});
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Scholar Research Assistant — 陈志远教授",
  description:
    "基于陈志远教授 15 篇公开论文炼化出的 AI 科研助手。通信安全、IIoT安全、UAV安全通信、可信计算、隐私保护。",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="zh"
      className={`${inter.variable} ${ibmPlexSerif.variable} ${jetbrainsMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `try{if(localStorage.getItem("theme")==="light")document.documentElement.classList.add("light")}catch(e){}`,
          }}
        />
      </head>
      <body className="min-h-full bg-[var(--bg-base)] text-[var(--text-primary)] flex flex-col">
        <Tooltip.Provider delayDuration={300} skipDelayDuration={400}>
          {children}
          <SearchDialog />
          <ScrollToTop />
        </Tooltip.Provider>
      </body>
    </html>
  );
}
