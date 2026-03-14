"use client";

import { Phone, X } from "lucide-react";
import { getCharacter } from "@/lib/characters";
import { Button } from "@/components/ui/button";

interface IncomingCallOverlayProps {
  characterId: string;
  symbol: string;
  onDismiss: () => void;
}

export function IncomingCallOverlay({
  characterId,
  symbol,
  onDismiss,
}: IncomingCallOverlayProps) {
  const character = getCharacter(characterId);
  if (!character) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{
        background: `radial-gradient(ellipse at center, ${character.color}15 0%, #0a0a0a 70%)`,
      }}
    >
      {/* Backdrop blur */}
      <div className="absolute inset-0 bg-[#0a0a0a]/80 backdrop-blur-sm" />

      <div className="relative z-10 flex flex-col items-center text-center space-y-8 p-8 max-w-sm">
        {/* Pulsing phone icon */}
        <div className="relative">
          <div
            className="w-24 h-24 rounded-full flex items-center justify-center"
            style={{
              backgroundColor: character.color + "20",
              border: `2px solid ${character.color}`,
            }}
          >
            <Phone
              className="w-10 h-10 animate-bounce"
              style={{ color: character.color }}
            />
          </div>
          {/* Pulse rings */}
          <div
            className="absolute inset-0 w-24 h-24 rounded-full animate-pulse-ring"
            style={{ border: `2px solid ${character.color}40` }}
          />
          <div
            className="absolute inset-0 w-24 h-24 rounded-full animate-pulse-ring"
            style={{
              border: `2px solid ${character.color}20`,
              animationDelay: "0.5s",
            }}
          />
        </div>

        {/* Character info */}
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-widest text-text-secondary">
            Incoming Call
          </p>
          <h2
            className="text-3xl font-bold"
            style={{ color: character.color }}
          >
            {character.name}
          </h2>
          <p className="text-sm text-text-secondary">{character.tagline}</p>
        </div>

        {/* Trade info */}
        <div
          className="px-4 py-2 rounded-full border text-sm font-mono-num font-semibold"
          style={{
            borderColor: character.color + "40",
            color: character.color,
          }}
        >
          {symbol}
        </div>

        <p className="text-text-secondary text-sm animate-pulse">
          Pick up your phone...
        </p>

        {/* Dismiss */}
        <Button
          onClick={onDismiss}
          variant="outline"
          className="border-[#333] text-text-secondary hover:text-text-primary hover:bg-[#1a1a1a]"
        >
          <X className="w-4 h-4 mr-1.5" />
          Dismiss
        </Button>
      </div>
    </div>
  );
}
