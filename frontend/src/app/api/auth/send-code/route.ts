import { NextResponse } from "next/server";

const ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID!;
const AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN!;
const VERIFY_SID = process.env.TWILIO_VERIFY_SERVICE_SID!;

export async function POST(req: Request) {
  try {
    const { phone } = await req.json();
    if (!phone) {
      return NextResponse.json({ error: "Phone required" }, { status: 400 });
    }

    // Normalize: add +1 if no country code
    const normalized = phone.startsWith("+") ? phone : `+1${phone.replace(/\D/g, "")}`;

    const res = await fetch(
      `https://verify.twilio.com/v2/Services/${VERIFY_SID}/Verifications`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          Authorization:
            "Basic " + Buffer.from(`${ACCOUNT_SID}:${AUTH_TOKEN}`).toString("base64"),
        },
        body: new URLSearchParams({ To: normalized, Channel: "sms" }),
      }
    );

    const data = await res.json();

    if (!res.ok) {
      console.error("Twilio send error:", data);
      return NextResponse.json(
        { error: data.message || "Failed to send code" },
        { status: res.status }
      );
    }

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("send-code error:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
