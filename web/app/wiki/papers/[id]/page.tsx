import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PaperCardDetail } from "@/components/papers/PaperCardDetail";
import { getPaperCard } from "@/lib/wiki-server";
import type { PaperData } from "@/lib/types";

interface PageProps { params: Promise<{ id: string }>; }

export const dynamic = "force-dynamic";

async function getPaper(id: string): Promise<PaperData | null> {
  const page = getPaperCard(id);
  if (!page) return null;
  const fm = page.frontmatter as Record<string, unknown>;
  return {
    paper_id: id,
    title: String(fm.title || ""),
    year: (fm.paper_year as number) ?? null,
    authors: (fm.authors as string[]) || [],
    venue: String(fm.venue || ""),
    abstract: "",
    body: page.body,
    frontmatter: page.frontmatter,
    evidence_ids: [],
    source_papers: (fm.source_papers as string[]) || [],
  };
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const paper = await getPaper(id);
  if (!paper) return { title: "Paper Not Found — Scholar Wiki" };
  return { title: `${paper.title} — Scholar Wiki` };
}

export default async function PaperDetailPage({ params }: PageProps) {
  const { id } = await params;
  const paper = await getPaper(id);
  if (!paper) notFound();
  return <PaperCardDetail paper={paper} />;
}
