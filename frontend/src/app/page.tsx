"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import { api } from "@/lib/api";
import { characters } from "@/lib/characters";
import { AsciiCanvas } from "@/components/landing/AsciiCanvas";
import { Eye, EyeOff, Check, ChevronDown, ExternalLink } from "lucide-react";

// ─── Step progress bar ──────────────────────────────────────────────
function StepBars({ current, total }: { current: number; total: number }) {
  return (
    <div className="flex gap-1.5 mb-6">
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          className="h-[3px] flex-1 rounded-full transition-colors duration-300"
          style={{
            backgroundColor:
              i < current ? "#555" : i === current ? "#fff" : "#1f1f1f",
          }}
        />
      ))}
    </div>
  );
}

// ─── Shared input component ─────────────────────────────────────────
function FormInput({
  id,
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  mono,
  toggleable,
}: {
  id: string;
  label: string;
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (v: string) => void;
  mono?: boolean;
  toggleable?: boolean;
}) {
  const [show, setShow] = useState(false);

  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-[11px] text-[#666] uppercase tracking-wider">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={toggleable ? (show ? "text" : "password") : type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required
          className={`w-full bg-[#0d0d0d] border border-[#252525] rounded-md px-3 py-2.5 text-[13px] text-[#eee] placeholder:text-[#333] outline-none focus:border-[#555] transition-colors ${mono ? "font-mono-num" : ""} ${toggleable ? "pr-10" : ""}`}
        />
        {toggleable && (
          <button
            type="button"
            onClick={() => setShow(!show)}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#444] hover:text-[#888] transition-colors"
          >
            {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>
    </div>
  );
}

// ─── Primary CTA button ─────────────────────────────────────────────
function PrimaryButton({
  children,
  disabled,
  loading,
  onClick,
  type = "submit",
}: {
  children: React.ReactNode;
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: "submit" | "button";
}) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className="w-full bg-white text-black font-semibold rounded-md py-2.5 text-[13px] transition-all hover:bg-[#ddd] disabled:opacity-30 disabled:cursor-not-allowed"
    >
      {loading ? (
        <span className="inline-block w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
      ) : (
        children
      )}
    </button>
  );
}

// ─── Step 0: Phone + OTP ────────────────────────────────────────────
function Step0({ onDone }: { onDone: (phone: string) => void }) {
  const [phone, setPhone] = useState("");
  const [phase, setPhase] = useState<"phone" | "code">("phone");
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const codeRefs = useRef<(HTMLInputElement | null)[]>([]);

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
      onDone(phone);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid code");
      setCode(["", "", "", "", "", ""]);
      codeRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  }

  if (phase === "code") {
    return (
      <div className="space-y-4">
        <div>
          <h2 className="text-[15px] font-semibold text-white">Verify your number</h2>
          <p className="text-[12px] text-[#666] mt-1">
            Code sent to <span className="font-mono-num text-[#999]">{phone}</span>
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
            className="text-white hover:underline"
          >
            Go back
          </button>
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSendCode} className="space-y-4">
      <div>
        <h2 className="text-[15px] font-semibold text-white">Create your account</h2>
        <p className="text-[12px] text-[#666] mt-1">Get your first call in under 3 minutes.</p>
      </div>
      <FormInput
        id="phone"
        label="Phone number"
        type="tel"
        placeholder="+1 555 000 0000"
        value={phone}
        onChange={setPhone}
        mono
      />
      {error && <p className="text-[#ff4444] text-[12px]">{error}</p>}
      <PrimaryButton disabled={!phone.trim()} loading={loading}>
        Send verification code
      </PrimaryButton>
      <p className="text-center text-[11px] text-[#444]">
        Already have an account?{" "}
        <a href="/login" className="text-[#ccc] hover:text-white hover:underline transition-colors">Log in</a>
      </p>
    </form>
  );
}

// ─── Step 1: Connect Liquid ─────────────────────────────────────────
function Step1({ onDone }: { onDone: () => void }) {
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [helpOpen, setHelpOpen] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.saveKeys(apiKey, apiSecret);
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save keys");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <h2 className="text-[15px] font-semibold text-white">Connect Liquid</h2>
        <p className="text-[12px] text-[#666] mt-1">
          We trade on your behalf — keys are AES-256 encrypted.
        </p>
      </div>
      <FormInput id="api-key" label="API Key" placeholder="lq_..." value={apiKey} onChange={setApiKey} mono toggleable />
      <FormInput id="api-secret" label="API Secret" placeholder="sk_..." value={apiSecret} onChange={setApiSecret} mono toggleable />

      <div className="rounded-md border border-[#1a1a1a] overflow-hidden">
        <button
          type="button"
          onClick={() => setHelpOpen(!helpOpen)}
          className="w-full flex items-center justify-between px-3 py-2 text-[11px] text-[#555] hover:text-[#999] transition-colors"
        >
          <span>How do I get my API key?</span>
          <ChevronDown className={`w-3.5 h-3.5 transition-transform ${helpOpen ? "rotate-180" : ""}`} />
        </button>
        {helpOpen && (
          <div className="px-3 pb-3 space-y-1.5 text-[11px] text-[#555]">
            <ol className="list-decimal list-inside space-y-1">
              <li>
                Sign up at{" "}
                <a href="https://app.liquid.com" target="_blank" rel="noopener noreferrer" className="text-[#ccc] hover:underline inline-flex items-center gap-0.5">
                  app.liquid.com <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </li>
              <li>Go to <span className="text-[#999]">Settings &rarr; API Tokens</span></li>
              <li>Click <span className="text-[#999]">Create API Token</span></li>
              <li>Enable <span className="text-[#999]">Trading</span> permissions, copy both values</li>
            </ol>
          </div>
        )}
      </div>

      <div className="p-2.5 rounded-md border border-[#1a1a1a] bg-[#0d0d0d]">
        <p className="text-[11px] text-[#555]">
          Your secret is never stored in plaintext. We only use it to sign orders.
        </p>
      </div>

      {error && <p className="text-[#ff4444] text-[12px]">{error}</p>}
      <PrimaryButton disabled={!apiKey.trim() || !apiSecret.trim()} loading={loading}>
        Connect
      </PrimaryButton>
    </form>
  );
}

// ─── Step 2: Choose character + call phone ──────────────────────────
function Step2({
  authPhone,
  onDone,
}: {
  authPhone: string;
  onDone: (characterId: string) => void;
}) {
  const [selected, setSelected] = useState("belfort");
  const [callPhone, setCallPhone] = useState(authPhone);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.updateMe({ phone: callPhone, character_id: selected });
      onDone(selected);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <h2 className="text-[15px] font-semibold text-white">Choose your caller</h2>
        <p className="text-[12px] text-[#666] mt-1">This voice will call you with trade pitches.</p>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {characters.map((c) => {
          const active = selected === c.id;
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => setSelected(c.id)}
              className="relative p-2.5 rounded-lg border text-left transition-all"
              style={{
                borderColor: active ? "#888" : "#1f1f1f",
                boxShadow: active ? "0 0 12px rgba(255,255,255,0.06)" : "none",
                background: active ? "rgba(255,255,255,0.03)" : "transparent",
              }}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: c.color }} />
                <span className="text-[12px] font-bold text-[#e0e0e0] truncate">{c.name}</span>
              </div>
              <p className="text-[10px] text-[#555] leading-tight">{c.tagline}</p>
              {active && (
                <div className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-white flex items-center justify-center">
                  <Check className="w-2.5 h-2.5 text-black" />
                </div>
              )}
            </button>
          );
        })}
      </div>
      <FormInput
        id="call-phone"
        label="We'll call this number"
        type="tel"
        placeholder="+1 555 000 0000"
        value={callPhone}
        onChange={setCallPhone}
        mono
      />
      {error && <p className="text-[#ff4444] text-[12px]">{error}</p>}
      <PrimaryButton disabled={!callPhone.trim()} loading={loading}>
        Continue
      </PrimaryButton>
    </form>
  );
}

// ─── Step 3: Success ────────────────────────────────────────────────
function Step3({ characterId, phone }: { characterId: string; phone: string }) {
  const router = useRouter();
  const character = characters.find((c) => c.id === characterId);

  return (
    <div className="flex flex-col items-center text-center space-y-5 py-2">
      <span className="text-[40px] text-white">&#x25C9;</span>
      <div className="space-y-2">
        <h2 className="text-[18px] font-bold text-white">Pitch is armed.</h2>
        <p className="text-[13px] font-mono-num text-[#aaa]">
          {character?.name} will call {phone}
        </p>
        <p className="text-[12px] text-[#555] leading-relaxed max-w-[260px]">
          The moment we detect a signal, your phone rings. Pick up. Say yes or no. We handle the rest.
        </p>
      </div>
      <PrimaryButton type="button" onClick={() => router.push("/dashboard")}>
        Go to dashboard &rarr;
      </PrimaryButton>
    </div>
  );
}

// ─── Main page ──────────────────────────────────────────────────────
export default function LandingPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [step, setStep] = useState(0);
  const [authPhone, setAuthPhone] = useState("");
  const [characterId, setCharacterId] = useState("belfort");

  useEffect(() => {
    if (isAuthenticated()) {
      router.replace("/dashboard");
    } else {
      setReady(true);
    }
  }, [router]);

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a]">
        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <AsciiCanvas />

      {/* Content layer — pointer-events-none so mouse passes through to ASCII canvas */}
      <div className="relative z-10 min-h-screen flex flex-col pointer-events-none">
        {/* Main content — centered vertically */}
        <div className="flex-1 flex items-center justify-center px-5 sm:px-8 py-10 sm:py-16">
          <div className="w-full max-w-[960px] flex flex-col lg:flex-row items-center lg:items-center gap-10 sm:gap-12 lg:gap-24">

            {/* Left — hero copy */}
            <div className="flex-1 max-w-[460px] text-center lg:text-left">
              <p className="font-mono-num text-[11px] text-[#888] tracking-[0.2em] uppercase mb-5 sm:mb-6">
                PITCH
              </p>
              <h1 className="text-[36px] sm:text-[48px] lg:text-[56px] font-semibold leading-[1.05] text-white mb-4 sm:mb-5">
                Your broker<br />
                never{" "}
                <span className="text-[#ccc]">sleeps.</span>
              </h1>
              <p className="text-[14px] sm:text-[15px] text-[#666] font-light leading-relaxed max-w-[380px] mx-auto lg:mx-0">
                AI calls your phone the moment a signal fires. Approve or reject. Trade executes automatically.
              </p>
            </div>

            {/* Right — onboarding card */}
            <div
              className="w-full sm:w-[360px] lg:w-[340px] shrink-0 rounded-xl p-6 sm:p-7 pointer-events-auto"
              style={{
                background: "rgba(10,10,10,0.92)",
                border: "1px solid #1f1f1f",
                backdropFilter: "blur(12px)",
              }}
            >
              <StepBars current={step} total={4} />

              {step === 0 && (
                <Step0
                  onDone={(phone) => {
                    setAuthPhone(phone);
                    setStep(1);
                  }}
                />
              )}
              {step === 1 && <Step1 onDone={() => setStep(2)} />}
              {step === 2 && (
                <Step2
                  authPhone={authPhone}
                  onDone={(cid) => {
                    setCharacterId(cid);
                    setStep(3);
                  }}
                />
              )}
              {step === 3 && <Step3 characterId={characterId} phone={authPhone} />}
            </div>
          </div>
        </div>

        {/* Bottom — trust line */}
        <div className="pb-6 sm:pb-8 flex justify-center">
          <div className="flex items-center gap-2">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#555] opacity-75" />
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#555]" />
            </span>
            <span className="font-mono-num text-[11px] text-[#444]">
              Powered by Liquid
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
