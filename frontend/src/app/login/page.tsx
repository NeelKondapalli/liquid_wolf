"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated, setPhone } from "@/lib/auth";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [phase, setPhase] = useState<"phone" | "code">("phone");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const codeRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (isAuthenticated()) router.replace("/dashboard");
  }, [router]);

  useEffect(() => {
    if (phase === "code") codeRefs.current[0]?.focus();
  }, [phase]);

  async function handleSendCode(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.sendCode(phone);
      setPhase("code");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send code");
    } finally {
      setLoading(false);
    }
  }

  function handleCodeInput(i: number, val: string) {
    if (!/^\d*$/.test(val)) return;
    const digit = val.slice(-1);
    const next = [...code];
    next[i] = digit;
    setCode(next);
    if (digit && i < 5) codeRefs.current[i + 1]?.focus();
    if (digit && i === 5 && next.every((d) => d)) verifyCode(next.join(""));
  }

  function handleCodeKeyDown(i: number, e: React.KeyboardEvent) {
    if (e.key === "Backspace" && !code[i] && i > 0) codeRefs.current[i - 1]?.focus();
  }

  function handleCodePaste(e: React.ClipboardEvent) {
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (pasted.length === 6) {
      e.preventDefault();
      setCode(pasted.split(""));
      codeRefs.current[5]?.focus();
      verifyCode(pasted);
    }
  }

  async function verifyCode(fullCode: string) {
    setError("");
    setLoading(true);
    try {
      await api.verifyCode(phone, fullCode);
      const normalized = phone.startsWith("+")
        ? phone
        : `+1${phone.replace(/\D/g, "")}`;
      setPhone(normalized);

      // Check if user has keys — if not, send to onboarding
      try {
        const { exists } = await api.checkUserExists(normalized);
        if (!exists) {
          router.push("/");
          return;
        }
        const { has_keys } = await api.checkUserHasKeys(normalized);
        if (!has_keys) {
          router.push("/");
          return;
        }
      } catch {
        // Backend unavailable — go to dashboard anyway
      }
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid code");
      setCode(["", "", "", "", "", ""]);
      codeRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a] px-5">
      <div className="w-full max-w-[340px]">
        <p className="font-mono-num text-[11px] text-[#888] tracking-[0.2em] uppercase text-center mb-8">
          PITCH
        </p>

        <div
          className="rounded-xl p-6 sm:p-7"
          style={{
            background: "rgba(17,17,17,1)",
            border: "1px solid #1f1f1f",
          }}
        >
          {phase === "phone" ? (
            <form onSubmit={handleSendCode} className="space-y-4">
              <div>
                <h2 className="text-[15px] font-semibold text-white">Welcome back</h2>
                <p className="text-[12px] text-[#666] mt-1">Log in with your phone number.</p>
              </div>
              <div className="space-y-1.5">
                <label htmlFor="login-phone" className="block text-[11px] text-[#666] uppercase tracking-wider">
                  Phone number
                </label>
                <input
                  id="login-phone"
                  type="tel"
                  placeholder="+1 555 000 0000"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                  className="w-full bg-[#0d0d0d] border border-[#252525] rounded-md px-3 py-2.5 text-[13px] text-[#eee] placeholder:text-[#333] outline-none focus:border-[#555] transition-colors font-mono-num"
                />
              </div>
              {error && <p className="text-[#ff4444] text-[12px]">{error}</p>}
              <button
                type="submit"
                disabled={!phone.trim() || loading}
                className="w-full bg-white text-black font-semibold rounded-md py-2.5 text-[13px] transition-all hover:bg-[#ddd] disabled:opacity-30 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="inline-block w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
                ) : (
                  "Send code"
                )}
              </button>
              <p className="text-center text-[11px] text-[#444]">
                Don&apos;t have an account?{" "}
                <a href="/" className="text-[#ccc] hover:text-white hover:underline transition-colors">Sign up</a>
              </p>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <h2 className="text-[15px] font-semibold text-white">Enter the code</h2>
                <p className="text-[12px] text-[#666] mt-1">
                  Sent to <span className="font-mono-num text-[#999]">{phone}</span>
                </p>
              </div>
              <div className="flex justify-center gap-1.5" onPaste={handleCodePaste}>
                {code.map((digit, i) => (
                  <input
                    key={i}
                    ref={(el) => { codeRefs.current[i] = el; }}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleCodeInput(i, e.target.value)}
                    onKeyDown={(e) => handleCodeKeyDown(i, e)}
                    className="w-10 h-12 text-center text-base font-mono-num font-bold bg-[#0d0d0d] border border-[#252525] rounded-md text-white focus:border-[#555] outline-none transition-colors"
                  />
                ))}
              </div>
              {loading && (
                <div className="flex justify-center">
                  <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                </div>
              )}
              {error && <p className="text-[#ff4444] text-[12px] text-center">{error}</p>}
              <p className="text-center text-[11px] text-[#444]">
                Wrong number?{" "}
                <button
                  type="button"
                  onClick={() => { setPhase("phone"); setCode(["", "", "", "", "", ""]); setError(""); }}
                  className="text-[#ccc] hover:text-white hover:underline transition-colors"
                >
                  Go back
                </button>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
