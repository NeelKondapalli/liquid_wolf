import type { Character } from "./types";

export const characters: Character[] = [
  {
    id: "belfort",
    name: "Jordan Belfort",
    tagline: "The Wolf of Wall Street",
    color: "#f5c518",
  },
  {
    id: "rick",
    name: "Rick Sanchez",
    tagline: "Interdimensional trader, Morty",
    color: "#00c8a0",
  },
  {
    id: "trump",
    name: "Donald Trump",
    tagline: "The greatest trader, believe me",
    color: "#e63946",
  },
];

export function getCharacter(id: string): Character | undefined {
  return characters.find((c) => c.id === id);
}
