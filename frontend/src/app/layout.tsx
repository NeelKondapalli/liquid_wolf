import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import { GeistPixelGrid } from "geist/font/pixel";
import "./globals.css";

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Pitch — Voice Trading Agent",
  description:
    "AI calls you to pitch trades. You approve over the phone. It executes automatically.",
  icons: {
    icon: "/favicon.svg",
  },
  openGraph: {
    title: "Pitch — Voice Trading Agent",
    description:
      "AI calls your phone the moment a signal fires. Approve or reject. Trade executes automatically.",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "Pitch — Voice Trading Agent",
    description:
      "AI calls your phone the moment a signal fires. Approve or reject. Trade executes automatically.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${GeistPixelGrid.variable} ${jetbrainsMono.variable} antialiased bg-[#0a0a0a] text-[#f0f0f0] min-h-screen`}
        style={{ fontFamily: "var(--font-geist-pixel-grid), monospace" }}
      >
        {children}
      </body>
    </html>
  );
}
