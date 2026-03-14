"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated, clearToken, getPhone } from "@/lib/auth";
import { api } from "@/lib/api";
import type { AccountSummary as AccountSummaryType, Call, Signal, User } from "@/lib/types";
import { AccountSummary } from "@/components/dashboard/AccountSummary";
import { PositionsTable } from "@/components/dashboard/PositionsTable";
import { CallHistory } from "@/components/dashboard/CallHistory";
import { SignalBanner } from "@/components/dashboard/SignalBanner";
import { EnableAlertsToggle } from "@/components/dashboard/EnableAlertsToggle";
import { IncomingCallOverlay } from "@/components/dashboard/IncomingCallOverlay";
import { CharacterAvatar } from "@/components/shared/CharacterAvatar";
import { LogOut, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

const POLL_INTERVAL = 5000;

export default function DashboardPage() {
  const router = useRouter();
  const [account, setAccount] = useState<AccountSummaryType | null>(null);
  const [calls, setCalls] = useState<Call[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [demoMode, setDemoMode] = useState(false);
  const [incomingCall, setIncomingCall] = useState<{
    characterId: string;
    symbol: string;
  } | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [accountData, callsData, signalsData, userData] = await Promise.all([
        api.getAccount(),
        api.getCalls(),
        api.getSignals(),
        api.getMe(),
      ]);
      setAccount(accountData);
      setCalls(callsData);
      setSignals(signalsData);
      setUser(userData);
    } catch {
      // Silently fail on poll errors
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/");
      return;
    }
    fetchData();
    const interval = setInterval(fetchData, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [router, fetchData]);

  // Shift+D handler for demo mode
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.shiftKey && e.key === "D") {
        setDemoMode((prev) => !prev);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  async function handleTriggerDemo() {
    try {
      await api.triggerDemo("BTC-PERP", "long", 0.87);
      setIncomingCall({
        characterId: user?.character_id ?? "belfort",
        symbol: "BTC-PERP",
      });
    } catch {
      // Demo trigger failed
    }
  }

  function handleLogout() {
    clearToken();
    router.replace("/");
  }

  return (
    <div className="min-h-screen">
      {/* Navbar */}
      <nav className="border-b border-surface-border bg-[#0a0a0a]/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <h1 className="text-lg font-bold text-white tracking-tight">
            Pitch
          </h1>
          <div className="flex items-center gap-4">
            {demoMode && (
              <Button
                onClick={handleTriggerDemo}
                size="sm"
                className="bg-warning/20 text-warning border border-warning/30 hover:bg-warning/30 text-xs"
              >
                <Zap className="w-3.5 h-3.5 mr-1" />
                Fire Demo Call
              </Button>
            )}
            {user && (
              <span className="text-xs text-text-secondary hidden sm:block">
                {user.first_name}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="text-text-secondary hover:text-text-primary transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Row 1: Account summary + alerts toggle */}
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <AccountSummary data={account} />
          </div>
          <div className="flex items-start gap-3">
            {user && (
              <>
                <EnableAlertsToggle initialEnabled={user.signal_enabled} />
                <CharacterAvatar
                  characterId={user.character_id ?? "belfort"}
                  size="lg"
                />
              </>
            )}
          </div>
        </div>

        {/* Signal banner */}
        <SignalBanner signals={signals} />

        {/* Row 2: Positions + Call history */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6">
          <PositionsTable positions={account?.positions ?? []} />
          <CallHistory calls={calls} />
        </div>

        {/* Demo mode indicator */}
        {demoMode && (
          <div className="fixed bottom-4 left-4 px-3 py-1.5 rounded-full bg-warning/20 border border-warning/30 text-warning text-xs font-semibold">
            DEMO MODE · Shift+D to toggle
          </div>
        )}
      </main>

      {/* Incoming call overlay */}
      {incomingCall && (
        <IncomingCallOverlay
          characterId={incomingCall.characterId}
          symbol={incomingCall.symbol}
          onDismiss={() => setIncomingCall(null)}
        />
      )}
    </div>
  );
}
