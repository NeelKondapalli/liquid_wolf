"use client";

import { useState } from "react";
import { Bell, BellOff } from "lucide-react";
import { api } from "@/lib/api";

interface EnableAlertsToggleProps {
  initialEnabled: boolean;
}

export function EnableAlertsToggle({
  initialEnabled,
}: EnableAlertsToggleProps) {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [loading, setLoading] = useState(false);

  async function handleToggle() {
    setLoading(true);
    try {
      await api.updateMe({ signal_enabled: !enabled });
      setEnabled(!enabled);
    } catch {
      // Revert on error — optimistic toggle not applied
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={handleToggle}
      disabled={loading}
      className={`
        flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all
        ${
          enabled
            ? "bg-white/10 text-white border border-white/20 glow-green"
            : "bg-[#1a1a1a] text-text-secondary border border-surface-border hover:border-[#333]"
        }
        ${loading ? "opacity-50 cursor-wait" : "cursor-pointer"}
      `}
    >
      {enabled ? (
        <Bell className="w-4 h-4" />
      ) : (
        <BellOff className="w-4 h-4" />
      )}
      {enabled ? "Alerts On" : "Alerts Off"}
    </button>
  );
}
