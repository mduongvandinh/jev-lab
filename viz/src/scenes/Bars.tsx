import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, mono, toneColor } from "../theme";
import { BarsScene } from "../types";
import { Frame, rise } from "../common";

// Bảng xếp hạng: thanh mọc lần lượt từ trên xuống
export const Bars: React.FC<{ readonly s: BarsScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const max = Math.max(...s.bars.map((b) => b.value));
  const step = Math.min(14, Math.floor((durationInFrames * 0.5) / s.bars.length));
  const rowH = Math.min(s.bars.some((b) => b.sub) ? 110 : 84, Math.floor(820 / s.bars.length));
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top: s.cookbook ? 410 : 360, left: 64, right: 64, display: "flex", flexDirection: "column" }}>
        {s.bars.map((b, i) => {
          const t = interpolate(frame, [10 + i * step, 10 + i * step + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={b.label} style={{ height: rowH, display: "flex", alignItems: "center", gap: 16, ...rise(frame, fps, 6 + i * step) }}>
              <div style={{ width: 280, display: "flex", flexDirection: "column", gap: 2 }}>
                <span style={{ fontSize: 27, fontWeight: 700, lineHeight: 1.15 }}>{b.label}</span>
                {b.sub ? <span style={{ fontSize: 18, color: C.muted, lineHeight: 1.2 }}>{b.sub}</span> : null}
              </div>
              <div style={{ flex: 1, height: Math.min(30, rowH - 30), background: C.line, borderRadius: 8, overflow: "hidden" }}>
                <div style={{ width: `${(b.value / max) * 100 * t}%`, height: "100%", background: toneColor(b.tone ?? "jev") }} />
              </div>
              <span style={{ width: 150, textAlign: "right", fontFamily: mono, fontSize: 26 }}>{b.text}</span>
            </div>
          );
        })}
        {s.note ? <div style={{ marginTop: 18, fontSize: 23, color: C.muted, lineHeight: 1.35 }}>{s.note}</div> : null}
      </div>
    </Frame>
  );
};
