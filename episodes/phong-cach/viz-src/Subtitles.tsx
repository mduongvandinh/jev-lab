import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, sans } from "./theme";

export type Caption = { readonly text: string; readonly start: number; readonly end: number };
export const LEAD = 8;

// Phụ đề theo mốc thời gian đo từ giọng đọc từng câu; đặt trên vùng giao diện Reels
export const Subtitles: React.FC<{ readonly captions: readonly Caption[] }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame - LEAD) / fps;
  const cur = captions.find((c, i) => t >= c.start && t < (captions[i + 1]?.start ?? c.end + 0.6));
  if (!cur) return null;
  return (
    <div style={{ position: "absolute", left: 56, right: 56, bottom: 470, display: "flex", justifyContent: "center", zIndex: 10 }}>
      <div style={{ fontFamily: sans, fontSize: 40, fontWeight: 600, lineHeight: 1.35, color: C.text, background: "rgba(0,0,0,0.72)", padding: "12px 26px", borderRadius: 14, textAlign: "center" }}>
        {cur.text}
      </div>
    </div>
  );
};
