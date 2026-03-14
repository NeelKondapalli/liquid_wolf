"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { CallDetail } from "@/lib/types";
import { getCharacter } from "@/lib/characters";
import { isAuthenticated } from "@/lib/auth";
import {
  ArrowLeft,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CallDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [call, setCall] = useState<CallDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/");
      return;
    }

    async function load() {
      try {
        const id = params.id as string;
        const data = await api.getCall(id);
        setCall(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load call");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [params.id, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-white animate-spin" />
      </div>
    );
  }

  if (error || !call) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-danger text-sm">{error || "Call not found"}</p>
        <Button
          variant="outline"
          onClick={() => router.push("/dashboard")}
          className="border-surface-border text-text-secondary"
        >
          Back to dashboard
        </Button>
      </div>
    );
  }

  const character = getCharacter(call.character_id);
  const isLong = call.signal_data.direction === "long";
  const timestamp = new Date(call.created_at).toLocaleString();

  return (
    <div className="min-h-screen">
      {/* Character banner */}
      <div
        className="h-32 relative"
        style={{
          background: `linear-gradient(135deg, ${character?.color ?? "#333"}30 0%, #0a0a0a 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto px-4 h-full flex items-end pb-4">
          <div>
            <button
              onClick={() => router.push("/dashboard")}
              className="flex items-center gap-1 text-xs text-text-secondary hover:text-text-primary transition-colors mb-3"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Dashboard
            </button>
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg"
                style={{
                  backgroundColor: (character?.color ?? "#333") + "20",
                  color: character?.color ?? "#888",
                  border: `1px solid ${(character?.color ?? "#333")}40`,
                }}
              >
                {character?.name.charAt(0) ?? "?"}
              </div>
              <div>
                <h1
                  className="text-lg font-bold"
                  style={{ color: character?.color }}
                >
                  {character?.name ?? "Unknown"}
                </h1>
                <p className="text-xs text-text-secondary">{timestamp}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Signal card */}
          <div className="bg-surface border border-surface-border rounded-lg p-5 space-y-4">
            <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Signal
            </h3>

            <div className="flex items-center gap-3">
              <span className="text-xl font-mono-num font-bold text-text-primary">
                {call.symbol}
              </span>
              <span
                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-bold ${
                  isLong
                    ? "bg-white/10 text-white"
                    : "bg-danger/15 text-danger"
                }`}
              >
                {isLong ? (
                  <ArrowUpRight className="w-3.5 h-3.5" />
                ) : (
                  <ArrowDownRight className="w-3.5 h-3.5" />
                )}
                {call.signal_data.direction.toUpperCase()}
              </span>
            </div>

            {/* Strength meter */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-text-secondary">Strength</span>
                <span className="font-mono-num text-white">
                  {(call.signal_data.strength * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-2 bg-[#1a1a1a] rounded-full overflow-hidden">
                <div
                  className="h-full bg-white rounded-full transition-all"
                  style={{ width: `${call.signal_data.strength * 100}%` }}
                />
              </div>
            </div>

            {/* OHLC */}
            <div className="grid grid-cols-2 gap-3 pt-2">
              {(
                [
                  ["Open", call.signal_data.open],
                  ["High", call.signal_data.high],
                  ["Low", call.signal_data.low],
                  ["Close", call.signal_data.close],
                ] as const
              ).map(([label, val]) => (
                <div
                  key={label}
                  className="bg-[#0a0a0a] border border-surface-border rounded p-2.5"
                >
                  <p className="text-[10px] text-text-secondary uppercase">
                    {label}
                  </p>
                  <p className="font-mono-num text-sm text-text-primary">
                    ${parseFloat(val).toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Outcome card */}
          <div className="bg-surface border border-surface-border rounded-lg p-5 space-y-4">
            <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Outcome
            </h3>

            {call.outcome === "executed" && (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                  <span className="text-lg font-bold text-white">
                    Trade Executed
                  </span>
                </div>
                {call.order_id && (
                  <div className="bg-[#0a0a0a] border border-surface-border rounded p-3">
                    <p className="text-[10px] text-text-secondary uppercase mb-1">
                      Order ID
                    </p>
                    <p className="font-mono-num text-sm text-text-primary">
                      {call.order_id}
                    </p>
                  </div>
                )}
              </div>
            )}

            {call.outcome === "passed" && (
              <div className="flex items-center gap-2">
                <XCircle className="w-5 h-5 text-text-secondary" />
                <span className="text-lg font-semibold text-text-secondary">
                  Passed on this one
                </span>
              </div>
            )}

            {call.outcome === "missed" && (
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-warning" />
                <span className="text-lg font-semibold text-warning">
                  Missed call
                </span>
              </div>
            )}

            {!call.outcome && (
              <div className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 text-warning animate-spin" />
                <span className="text-lg font-semibold text-warning animate-pulse">
                  In progress...
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
