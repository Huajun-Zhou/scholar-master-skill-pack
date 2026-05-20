import { NextRequest, NextResponse } from "next/server";
import { getPaperCard } from "@/lib/wiki-server";

export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const paper = getPaperCard(id);
  if (!paper) return NextResponse.json({ error: "not found" }, { status: 404 });
  return NextResponse.json(paper);
}
