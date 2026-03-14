"use client";

import type { Signal } from "@/lib/types";
import { ArrowUpRight, ArrowDownRight, Activity } from "lucide-react";

interface SignalBannerProps {
  signals: Signal[];
}

export function SignalBanner({ signals }: SignalBannerProps) {
  if (signals.length === 0) return null;

  return (
    <div className="bg-surface border border-surface-border rounded-lg p-3 overflow-x-auto">
      <div className="flex items-center gap-3 min-w-max">
        <div className="flex items-center gap-1.5 text-xs text-text-secondary shrink-0">
          <Activity className="w-3.5 h-3.5 text-white animate-pulse" />
          <span>Active Signals</span>
        </div>
        {signals.map((signal) => (
          <div
            key={signal.symbol + signal.triggered_at}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#1a1a1a] border border-[#333]"
          >
            <span className="font-mono-num text-xs font-semibold text-text-primary">
              {signal.symbol}
            </span>
            {signal.direction === "long" ? (
              <ArrowUpRight className="w-3.5 h-3.5 text-white" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5 text-danger" />
            )}
            <div className="flex gap-px">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className={`w-1 h-3 rounded-full ${
                    i < Math.round(signal.strength * 5)
                      ? "bg-white"
                      : "bg-[#333]"
                  }`}
                />
              ))}
            </div>
            <span className="text-[10px] text-text-secondary">
              Watching...
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
