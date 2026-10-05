import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, toneColor } from "../theme";
import { JudgeScene } from "../types";
import { CardView, Frame, Meter, pop } from "../common";

// Lần lượt từng ứng viên: thẻ dữ liệu, các chỉ số, rồi đóng dấu đạt / loại
export const Judge: React.FC<{ readonly s: JudgeScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const per = Math.floor(durationInFrames / s.items.length);
  const i = Math.min(s.items.length - 1, Math.floor(frame / per));
  const local = frame - i * per;
  const it = s.items[i];
  const t = interpolate(local, [4, per * 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const stamp = pop(frame, fps, i * per + per * 0.6);
  const top = s.cookbook ? 410 : 370;
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top, left: 56, right: 56, background: C.panel, borderRadius: 26, padding: 30, border: `2px solid ${C.line}`, display: "flex", flexDirection: "column", gap: 22 }}>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <CardView card={it.card} w={900} h={210} />
        </div>
        {it.metrics.map((m) => (
          <Meter key={m.label} label={m.label} value={m.value} text={m.text} color={toneColor(m.tone)} t={t} />
        ))}
      </div>
      <div style={{ position: "absolute", top: top + 300 + it.metrics.length * 50, left: 0, right: 0, textAlign: "center", opacity: stamp, transform: `scale(${interpolate(stamp, [0, 1], [1.6, 1])}) rotate(-5deg)` }}>
        <span style={{ display: "inline-block", fontSize: 58, fontWeight: 800, letterSpacing: 3, padding: "6px 28px", borderRadius: 14, border: `6px solid ${it.pass ? C.good : C.bad}`, color: it.pass ? C.good : C.bad }}>{it.stamp}</span>
      </div>
      <div style={{ position: "absolute", top: top - 40, right: 64, fontSize: 22, color: C.muted }}>{i + 1}/{s.items.length}</div>
    </Frame>
  );
};
