import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, sans } from "../theme";

export const pop = (frame: number, fps: number, delay = 0) => spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 16 });
export const rise = (frame: number, fps: number, delay = 0) => {
  const p = pop(frame, fps, delay);
  return { opacity: p, transform: `translateY(${interpolate(p, [0, 1], [24, 0])}px)` };
};

// Tiêu đề cảnh + dòng chú thích ở đáy (khung dọc 1080x1920, chừa vùng an toàn của Reels)
export const Frame: React.FC<{ readonly step: string; readonly title: string; readonly captionOff?: string; readonly children: React.ReactNode }> = ({ step, title, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: sans, color: C.text }}>
      <div style={{ position: "absolute", top: 150, left: 64, right: 64, ...rise(frame, fps) }}>
        <div style={{ fontSize: 26, fontWeight: 800, color: C.jev, letterSpacing: 2 }}>{step}</div>
        <div style={{ fontSize: 58, fontWeight: 800, lineHeight: 1.12, marginTop: 6 }}>{title}</div>
      </div>
      {children}
      {/* captionOff: chú thích tĩnh không hiển thị, lời đọc đã có phụ đề */}
    </div>
  );
};

export const Chip: React.FC<{ readonly text: string; readonly color?: string; readonly size?: number }> = ({ text, color = C.jev, size = 22 }) => (
  <span style={{ display: "inline-block", fontSize: size, fontWeight: 700, color: "#fff", background: color, borderRadius: 999, padding: "4px 12px", whiteSpace: "nowrap" }}>{text}</span>
);
