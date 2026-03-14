"use client";

import Link from "next/link";
import type { Call } from "@/lib/types";
import { CharacterAvatar } from "@/components/shared/CharacterAvatar";
import { ChevronRight } from "lucide-react";

interface CallHistoryProps {
  calls: Call[];
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

export function CallHistory({ calls }: CallHistoryProps) {
  return (
    <div className="bg-surface border border-surface-border rounded-lg overflow-hidden">
      <div className="p-4 border-b border-surface-border">
        <h3 className="text-sm font-semibold text-text-primary">
          Recent Calls
        </h3>
      </div>

      {calls.length === 0 ? (
        <div className="p-8 text-center">
          <p className="text-text-secondary text-sm">
            No calls yet · Enable alerts to get started
          </p>
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
