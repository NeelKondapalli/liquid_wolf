import { NextResponse } from "next/server";

const ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID!;
const AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN!;
const VERIFY_SID = process.env.TWILIO_VERIFY_SERVICE_SID!;
const JWT_SECRET = process.env.JWT_SECRET || "pitch_default_secret";

export async function POST(req: Request) {
  try {
    const { phone, code } = await req.json();
    if (!phone || !code) {
      return NextResponse.json(
        { error: "Phone and code required" },
        { status: 400 }
      );
    }

    const normalized = phone.startsWith("+") ? phone : `+1${phone.replace(/\D/g, "")}`;

    const res = await fetch(
      `https://verify.twilio.com/v2/Services/${VERIFY_SID}/VerificationCheck`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          Authorization:
            "Basic " + Buffer.from(`${ACCOUNT_SID}:${AUTH_TOKEN}`).toString("base64"),
        },
        body: new URLSearchParams({ To: normalized, Code: code }),
      }
    );

    const data = await res.json();

    if (!res.ok || data.status !== "approved") {
      return NextResponse.json(
        { error: "Invalid code" },
        { status: 401 }
      );
    }

    // Generate a simple JWT-like token (base64 encoded, signed with HMAC)
    const payload = {
      phone: normalized,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60, // 7 days
    };

    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(JWT_SECRET),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );

    const headerB64 = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
    const payloadB64 = btoa(JSON.stringify(payload));
    const signatureBuffer = await crypto.subtle.sign(
      "HMAC",
      key,
      encoder.encode(`${headerB64}.${payloadB64}`)
    );
    const signatureB64 = btoa(
      String.fromCharCode(...new Uint8Array(signatureBuffer))
    );

    const token = `${headerB64}.${payloadB64}.${signatureB64}`;

    return NextResponse.json({ access_token: token });
  } catch (err) {
    console.error("verify error:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
