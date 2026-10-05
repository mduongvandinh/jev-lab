import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { AXIS_VI, C, mono, sans, vi } from "../theme";
import { VizData } from "../types";
import { Chip, rise } from "./common";

// Lộ diện phong cách mới: tên, bảng màu, quy tắc; ghi rõ phạm vi "chưa xuất hiện trong N ảnh đã quét"
export const Reveal: React.FC<{ readonly data: VizData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const w = data.winner;
  return (
    <AbsoluteFill style={{ padding: "150px 64px 640px", fontFamily: sans, color: C.text, gap: 22, background: `radial-gradient(circle at 80% 15%, ${w.palette[0]}55, transparent 50%), radial-gradient(circle at 10% 90%, ${w.palette[1] ?? C.jev}44, transparent 50%)` }}>
      <div style={{ fontSize: 26, fontWeight: 800, color: C.jev, letterSpacing: 2, ...rise(frame, fps) }}>KẾT QUẢ · PHONG CÁCH MỚI</div>
      <div style={{ fontSize: 92, fontWeight: 800, lineHeight: 1.02, ...rise(frame, fps, 6) }}>{w.name}</div>
      <div style={{ fontSize: 38, lineHeight: 1.35, color: C.text, ...rise(frame, fps, 12) }}>{w.tagline}</div>
      <div style={{ display: "flex", gap: 12, ...rise(frame, fps, 18) }}>
        {w.palette.map((h) => (
          <div key={h} style={{ flex: 1, height: 88, borderRadius: 16, background: h, display: "flex", alignItems: "flex-end", padding: 10 }}>
            <span style={{ fontFamily: mono, fontSize: 18, background: "rgba(0,0,0,0.5)", padding: "2px 8px", borderRadius: 6 }}>{h}</span>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, ...rise(frame, fps, 24) }}>
        {Object.entries(w.combo).map(([ax, v]) => (
          <Chip key={ax} text={`${AXIS_VI[ax]}: ${vi(v)}`} size={24} />
        ))}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {w.rules.slice(0, 4).map((r, i) => (
          <div key={r} style={{ display: "flex", gap: 14, fontSize: 32, lineHeight: 1.3, ...rise(frame, fps, 32 + i * 8) }}>
            <span style={{ color: w.palette[0], fontWeight: 800 }}>◆</span>
            <span>{r}</span>
          </div>
        ))}
      </div>
      <div style={{ fontSize: 22, color: C.muted, lineHeight: 1.35, ...rise(frame, fps, 60) }}>
        Chưa xuất hiện trong {data.kept.toLocaleString("vi-VN")} ảnh đã phân tích từ {data.source}; Jev chấm mạch lạc và mới lạ.
      </div>
    </AbsoluteFill>
  );
};
