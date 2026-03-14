"use client";

import type { Position } from "@/lib/types";
import { TrendingUp, TrendingDown } from "lucide-react";

interface PositionsTableProps {
  positions: Position[];
  loading?: boolean;
}

function formatNum(val: string, prefix = ""): string {
  const num = parseFloat(val);
  return prefix + num.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function pnlColor(val: string): string {
  const num = parseFloat(val);
  if (num > 0) return "text-white";
  if (num < 0) return "text-danger";
  return "text-text-secondary";
}

function pnlSign(val: string): string {
  const num = parseFloat(val);
  if (num > 0) return "+$" + Math.abs(num).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (num < 0) return "-$" + Math.abs(num).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return "$0.00";
}

export function PositionsTable({ positions, loading }: PositionsTableProps) {
  if (loading) {
    return (
      <div className="bg-surface border border-surface-border rounded-lg overflow-hidden">
        <div className="p-4 border-b border-surface-border">
          <div className="h-4 w-20 bg-[#1a1a1a] rounded animate-pulse" />
        </div>
        <div className="divide-y divide-surface-border">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center gap-4 p-3">
              <div className="h-4 w-20 bg-[#1a1a1a] rounded animate-pulse" />
              <div className="h-5 w-14 bg-[#1a1a1a] rounded animate-pulse" />
              <div className="flex-1" />
              <div className="h-4 w-16 bg-[#1a1a1a] rounded animate-pulse" />
              <div className="h-4 w-16 bg-[#1a1a1a] rounded animate-pulse" />
              <div className="h-4 w-16 bg-[#1a1a1a] rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (positions.length === 0) {
    return (
      <div className="bg-surface border border-surface-border rounded-lg p-8 text-center">
        <p className="text-[32px] mb-3 opacity-30">&#x25CE;</p>
        <p className="text-text-secondary text-sm">No open positions</p>
        <p className="text-[#333] text-xs mt-1">Positions will appear here when a trade executes</p>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-surface-border rounded-lg overflow-hidden">
      <div className="p-4 border-b border-surface-border">
        <h3 className="text-sm font-semibold text-text-primary">Positions</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-text-secondary border-b border-surface-border">
              <th className="text-left p-3 font-medium">Symbol</th>
              <th className="text-left p-3 font-medium">Side</th>
              <th className="text-right p-3 font-medium">Size</th>
              <th className="text-right p-3 font-medium">Entry</th>
              <th className="text-right p-3 font-medium">Mark</th>
              <th className="text-right p-3 font-medium">PnL</th>
              <th className="text-right p-3 font-medium">Leverage</th>
              <th className="text-right p-3 font-medium">Liq Price</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos) => (
              <tr
                key={pos.symbol}
                className="border-b border-surface-border last:border-0 hover:bg-[#161616] transition-colors"
              >
                <td className="p-3 font-semibold text-text-primary font-mono-num">
                  {pos.symbol}
                </td>
                <td className="p-3">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold ${
                      pos.side === "long"
                        ? "bg-white/10 text-white"
                        : "bg-danger/15 text-danger"
                    }`}
                  >
                    {pos.side === "long" ? (
                      <TrendingUp className="w-3 h-3" />
                    ) : (
                      <TrendingDown className="w-3 h-3" />
                    )}
                    {pos.side.toUpperCase()}
                  </span>
                </td>
                <td className="p-3 text-right font-mono-num text-text-primary">
                  {pos.size}
                </td>
                <td className="p-3 text-right font-mono-num text-text-secondary">
                  {formatNum(pos.entry_price, "$")}
                </td>
                <td className="p-3 text-right font-mono-num text-text-primary">
                  {formatNum(pos.mark_price, "$")}
                </td>
                <td
                  className={`p-3 text-right font-mono-num font-semibold ${pnlColor(pos.unrealized_pnl)}`}
                >
                  {pnlSign(pos.unrealized_pnl)}
                </td>
                <td className="p-3 text-right font-mono-num text-text-secondary">
                  {pos.leverage}x
                </td>
                <td className="p-3 text-right font-mono-num text-text-secondary">
                  {formatNum(pos.liquidation_price, "$")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
