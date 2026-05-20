import { NextRequest, NextResponse } from "next/server";
import { getWikiPage, getWikiIndex } from "@/lib/wiki-server";

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  let wikiPath = url.searchParams.get("path") || "";

  if (!wikiPath || wikiPath === "index") {
    return NextResponse.json(getWikiIndex());
  }

  const page = getWikiPage(wikiPath);
  if (!page) {
    return NextResponse.json({ error: "not found" }, { status: 404 });
  }
  return NextResponse.json(page);
}
