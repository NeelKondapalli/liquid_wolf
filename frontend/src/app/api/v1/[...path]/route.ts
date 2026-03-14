import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.API_URL || "http://localhost:5000";
const API_KEY = process.env.BACKEND_API_KEY || "";

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const target = `${BACKEND_URL}/api/v1/${path.join("/")}`;

  try {
    const body = await req.text();
    const res = await fetch(target, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
      },
      body,
    });

    const data = await res.text();
    return new NextResponse(data, {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("Backend proxy error:", err);
    return NextResponse.json(
      { success: false, error: "Backend unavailable" },
      { status: 502 }
    );
  }
}
