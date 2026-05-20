import { NextResponse } from "next/server";
import { listAllPapers, getPaperCard } from "@/lib/wiki-server";

export async function GET() {
  const papers = listAllPapers();
  return NextResponse.json(papers.map((p) => ({
    paper_id: p.paper_id,
    title: p.title,
    year: p.year,
    authors: p.authors || [],
    venue: p.venue || "",
    n_pages: p.n_pages,
  })));
}
