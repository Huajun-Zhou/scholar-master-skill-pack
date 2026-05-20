import { NextResponse } from "next/server";
import { listThinkingModels } from "@/lib/wiki-server";

export async function GET() {
  return NextResponse.json(listThinkingModels());
}
