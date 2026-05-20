import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PaperCardDetail } from "@/components/papers/PaperCardDetail";
import type { PaperData } from "@/lib/types";

interface PageProps {
  params: Promise<{ id: string }>;
}

async function getPaper(id: string): Promise<PaperData | null> {
  try {
    const res = await fetch(
      `/api/papers/${id}`,
      { next: { revalidate: 60 } }
    );
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { id } = await params;
  const paper = await getPaper(id);

  if (!paper) {
    return { title: "Paper Not Found — Scholar Wiki" };
  }

  return {
    title: `${paper.title} — Scholar Wiki`,
    description: paper.abstract
      ? paper.abstract.slice(0, 160)
      : `Paper card for ${paper.title} by ${paper.authors?.join(", ") || "Zhiyuan Chen"}`,
  };
}

export default async function PaperDetailPage({ params }: PageProps) {
  const { id } = await params;
  const paper = await getPaper(id);

  if (!paper) {
    notFound();
  }

  return <PaperCardDetail paper={paper} />;
}
