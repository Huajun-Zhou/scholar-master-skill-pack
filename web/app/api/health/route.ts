import { NextResponse } from "next/server";
import { listAllPapers } from "@/lib/wiki-server";

export async function GET() {
  const papers = listAllPapers();
  return NextResponse.json({ status: "ok", papers: papers.length });
}
