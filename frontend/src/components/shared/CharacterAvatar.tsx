"use client";

import { getCharacter } from "@/lib/characters";

interface CharacterAvatarProps {
  characterId: string;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "w-6 h-6 text-xs",
  md: "w-8 h-8 text-sm",
  lg: "w-12 h-12 text-lg",
};

export function CharacterAvatar({
  characterId,
  size = "md",
}: CharacterAvatarProps) {
  const character = getCharacter(characterId);
  if (!character) return null;

  const initial = character.name.charAt(0).toUpperCase();

  return (
    <div
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center font-bold shrink-0`}
      style={{
        backgroundColor: character.color + "20",
        color: character.color,
        border: `1px solid ${character.color}40`,
      }}
    >
      {initial}
    </div>
  );
}
