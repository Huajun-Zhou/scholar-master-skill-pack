import { NextRequest, NextResponse } from "next/server";
import { getWikiPage, getWikiIndex } from "@/lib/wiki-server";

export async function GET(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  if (!path || path.length === 0) {
    return NextResponse.json(getWikiIndex());
  }
  const wikiPath = path.join("/");
  const page = getWikiPage(wikiPath);
  if (!page) return NextResponse.json({ error: "not found" }, { status: 404 });
  return NextResponse.json(page);
}
