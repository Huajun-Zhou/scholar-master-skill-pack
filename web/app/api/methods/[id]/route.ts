import { NextRequest, NextResponse } from "next/server";
import { getMethod } from "@/lib/wiki-server";

export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const method = getMethod(id);
  if (!method) return NextResponse.json({ error: "not found" }, { status: 404 });
  return NextResponse.json(method);
}
