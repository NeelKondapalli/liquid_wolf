"use client";

import dynamic from "next/dynamic";

const Video2Ascii = dynamic(() => import("video2ascii"), { ssr: false });

export function AsciiCanvas() {
  return (
    <>
      <div className="fixed inset-0 w-full h-full">
        <Video2Ascii
          src="/belfort.mp4"
          numColumns={160}
          colored={true}
          brightness={0.6}
          autoPlay={true}
          isPlaying={true}
          enableMouse={true}
          trailLength={24}
          enableRipple={true}
          rippleSpeed={40}
          charset="detailed"
          className="w-full h-full"
        />
      </div>
      {/* Vignette overlay */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 30%, #0a0a0a 100%)",
        }}
      />
      {/* Scanlines overlay */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px)",
          opacity: 0.55,
        }}
      />
    </>
  );
}
