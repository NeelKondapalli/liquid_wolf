"use client";

import Link from "next/link";
import type { Call } from "@/lib/types";
import { CharacterAvatar } from "@/components/shared/CharacterAvatar";
import { ChevronRight } from "lucide-react";

interface CallHistoryProps {
  calls: Call[];
  loading?: boolean;
}

function timeAgo(dateStr: string): string {
  const seconds = Math.floor(
    (Date.now() - new Date(dateStr).getTime()) / 1000
  );
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

const outcomeBadge: Record<string, { label: string; className: string }> = {
  executed: {
    label: "EXECUTED",
    className: "bg-white/10 text-white",
  },
  passed: {
    label: "PASSED",
    className: "bg-[#333]/50 text-text-secondary",
  },
  missed: {
    label: "MISSED",
    className: "bg-warning/15 text-warning",
  },
};

export function CallHistory({ calls, loading }: CallHistoryProps) {
  if (loading) {
    return (
      <div className="bg-surface border border-surface-border rounded-lg overflow-hidden">
        <div className="p-4 border-b border-surface-border">
          <div className="h-4 w-24 bg-[#1a1a1a] rounded animate-pulse" />
        </div>
        <div className="divide-y divide-surface-border">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center gap-3 p-3">
              <div className="w-8 h-8 rounded-full bg-[#1a1a1a] animate-pulse" />
              <div className="flex-1 space-y-1.5">
                <div className="h-3.5 w-20 bg-[#1a1a1a] rounded animate-pulse" />
                <div className="h-3 w-12 bg-[#1a1a1a] rounded animate-pulse" />
              </div>
              <div className="h-4 w-16 bg-[#1a1a1a] rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-surface-border rounded-lg overflow-hidden">
      <div className="p-4 border-b border-surface-border">
        <h3 className="text-sm font-semibold text-text-primary">
          Recent Calls
        </h3>
      </div>

      {calls.length === 0 ? (
        <div className="p-8 text-center">
          <p className="text-[32px] mb-3 opacity-30">&#x260E;</p>
          <p className="text-text-secondary text-sm">No calls yet</p>
          <p className="text-[#333] text-xs mt-1">Your AI broker will call when a signal fires</p>
        </div>
      ) : (
        <div className="divide-y divide-surface-border">
          {calls.map((call) => {
            const badge = outcomeBadge[call.outcome ?? "missed"];
            return (
              <Link
                key={call.id}
                href={`/calls/${call.id}`}
                className="flex items-center gap-3 p-3 hover:bg-[#161616] transition-colors group"
              >
                <CharacterAvatar characterId={call.character_id} size="sm" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-mono-num text-text-primary font-semibold">
                    {call.symbol}
                  </p>
                  <p className="text-xs text-text-secondary">
                    {timeAgo(call.created_at)}
                  </p>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${badge.className}`}
                >
                  {badge.label}
                </span>
                <ChevronRight className="w-4 h-4 text-[#333] group-hover:text-text-secondary transition-colors" />
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
