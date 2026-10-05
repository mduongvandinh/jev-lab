import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, mono, sans } from "../theme";
import { IntroScene } from "../types";
import { rise, useAccent } from "../common";

export const Intro: React.FC<{ readonly s: IntroScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = useAccent();
  return (
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 72px 420px", fontFamily: sans, color: C.text, gap: 28 }}>
      <div style={{ fontSize: 30, fontWeight: 800, color: accent, letterSpacing: 3, ...rise(frame, fps) }}>{s.kicker}</div>
      <div style={{ fontSize: 88, fontWeight: 800, lineHeight: 1.06, ...rise(frame, fps, 6) }}>{s.headline}</div>
      <div style={{ fontSize: 40, color: C.muted, lineHeight: 1.35, ...rise(frame, fps, 14) }}>{s.sub}</div>
      <div style={{ fontFamily: mono, fontSize: 26, color: C.muted, ...rise(frame, fps, 22) }}>fb.com/m.duongvandinh</div>
    </AbsoluteFill>
  );
};
