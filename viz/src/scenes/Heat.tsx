import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, fmt, mono } from "../theme";
import { HeatScene } from "../types";
import { Frame, useAccent } from "../common";

const rgba = (hex: string, a: number) => {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  return `rgba(${r},${g},${b},${a})`;
};

// Bản đồ nhiệt lấp dần từng ô; ô nổi bật sáng viền vàng ở nửa sau cảnh
export const Heat: React.FC<{ readonly s: HeatScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const accent = useAccent();
  const flat = s.values.flat();
  const max = Math.max(...flat);
  const min = Math.min(...flat);
  const total = flat.length;
  const filled = interpolate(frame, [10, durationInFrames * 0.5], [0, total], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const glow = frame > durationInFrames * 0.55;
  const labelW = 190;
  const cell = Math.min(110, Math.floor((1000 - labelW) / s.cols.length));
  const rowH = Math.min(cell, Math.floor(700 / s.rows.length));
  const isHi = (i: number, j: number) => (s.highlight ?? []).some(([a, b]) => a === i && b === j);
  const top = s.cookbook ? 400 : 350;
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top, left: 40 }}>
        <div style={{ display: "flex", marginLeft: labelW }}>
          {s.cols.map((c) => (
            <div key={c} style={{ width: cell, textAlign: "center", fontSize: 20, color: C.muted }}>{c}</div>
          ))}
        </div>
        {s.rows.map((r, i) => (
          <div key={r} style={{ display: "flex", alignItems: "center" }}>
            <div style={{ width: labelW, fontSize: 22, color: C.muted, textAlign: "right", paddingRight: 12 }}>{r}</div>
            {s.cols.map((c, j) => {
              const n = s.values[i][j];
              const shown = i * s.cols.length + j < filled;
              const hi = glow && isHi(i, j);
              const a = max === min ? 0.6 : 0.12 + 0.88 * ((n - min) / (max - min));
              return (
                <div key={c} style={{
                  width: cell - 4, height: rowH - 4, margin: 2, borderRadius: 6, background: shown ? rgba(accent, a) : "transparent",
                  border: hi ? `3px solid ${C.warn}` : `1px solid ${C.line}`, boxShadow: hi ? `0 0 ${10 + 8 * Math.sin(frame / 5)}px ${C.warn}` : "none",
                  display: "flex", alignItems: "center", justifyContent: "center", fontFamily: mono, fontSize: rowH > 50 ? 18 : 15, color: "#fff",
                }}>
                  {shown ? fmt(n, s.digits ?? 0) : ""}
                </div>
              );
            })}
          </div>
        ))}
        <div style={{ marginTop: 14, marginLeft: labelW, fontSize: 22, color: C.muted, maxWidth: 1000 - labelW }}>{s.legend}</div>
      </div>
    </Frame>
  );
};
