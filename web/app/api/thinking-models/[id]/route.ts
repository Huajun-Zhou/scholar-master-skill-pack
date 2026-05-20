import { NextRequest, NextResponse } from "next/server";
import { getThinkingModel } from "@/lib/wiki-server";

export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const model = getThinkingModel(id);
  if (!model) return NextResponse.json({ error: "not found" }, { status: 404 });
  return NextResponse.json(model);
}
