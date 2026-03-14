"use client";

import type { AccountSummary as AccountSummaryType } from "@/lib/types";

interface AccountSummaryProps {
  data: AccountSummaryType | null;
}

function StatCard({
  label,
  value,
  color = "text-white",
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="bg-surface border border-surface-border rounded-lg p-4">
      <p className="text-xs text-text-secondary mb-1">{label}</p>
      <p className={`text-xl font-mono-num ${color}`}>{value}</p>
    </div>
  );
}

function formatUsd(val: string): string {
  const num = parseFloat(val);
  return "$" + num.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function AccountSummary({ data }: AccountSummaryProps) {
  if (!data) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-surface border border-surface-border rounded-lg p-4 animate-pulse"
          >
            <div className="h-3 w-16 bg-[#1a1a1a] rounded mb-2" />
            <div className="h-6 w-24 bg-[#1a1a1a] rounded" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <StatCard label="Total Equity" value={formatUsd(data.equity)} />
      <StatCard label="Available" value={formatUsd(data.available_balance)} />
      <StatCard
        label="Margin Used"
        value={formatUsd(data.margin_used)}
        color="text-warning"
      />
      <StatCard
        label="Open Positions"
        value={String(data.positions.length)}
        color="text-text-primary"
      />
    </div>
  );
}
