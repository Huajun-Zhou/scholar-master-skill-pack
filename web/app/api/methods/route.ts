import { NextResponse } from "next/server";
import { listMethods, getMethod } from "@/lib/wiki-server";

export async function GET() {
  return NextResponse.json(listMethods());
}
