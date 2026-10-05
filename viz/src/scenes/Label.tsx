import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, fmt, mono, toneColor } from "../theme";
import { LabelScene } from "../types";
import { CardView, Frame, rise, useAccent } from "../common";

// Vài ví dụ thật: dữ liệu bên trái, đáp án Jev kèm xác suất bên phải; cuối cảnh là biểu đồ tổng
export const Label: React.FC<{ readonly s: LabelScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const accent = useAccent();
  const ex = s.examples.slice(0, 4);
  const top = s.cookbook ? 410 : 360;
  const rowH = s.tally ? 150 : 200;
  const maxBar = Math.max(1, ...(s.tally?.bars ?? []).map((b) => b.value));
  const t = interpolate(frame, [durationInFrames * 0.45, durationInFrames * 0.75], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top, left: 48, right: 48, display: "flex", flexDirection: "column", gap: 14 }}>
        {ex.map((e, i) => (
          <div key={i} style={{ display: "flex", gap: 16, height: rowH, background: C.panel, borderRadius: 18, padding: 10, border: `1.5px solid ${accent}55`, ...rise(frame, fps, 8 + i * 12) }}>
            <CardView card={e.card} w={300} h={rowH - 20} compact />
            <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", gap: 6 }}>
              {e.answers.map((a, j) => (
                <div key={a.q} style={{ display: "flex", alignItems: "baseline", gap: 10, ...rise(frame, fps, 14 + i * 12 + j * 4) }}>
                  <span style={{ width: 150, fontSize: 19, color: C.muted, flexShrink: 0 }}>{a.q}</span>
                  <span style={{ fontSize: 23, fontWeight: 800, color: toneColor(a.tone) }}>{a.text}</span>
                  {a.prob !== undefined ? <span style={{ fontFamily: mono, fontSize: 18, color: C.muted }}>{Math.round(a.prob * 100)}%</span> : null}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      {s.tally ? (
        <div style={{ position: "absolute", top: top + ex.length * (rowH + 14) + 16, left: 64, right: 64, opacity: t }}>
          <div style={{ fontSize: 24, fontWeight: 800, color: C.muted, marginBottom: 8 }}>{s.tally.title}</div>
          {s.tally.bars.slice(0, 5).map((b) => (
            <div key={b.label} style={{ display: "flex", alignItems: "center", gap: 14, height: 38 }}>
              <span style={{ width: 260, fontSize: 23 }}>{b.label}</span>
              <div style={{ flex: 1, height: 18, background: C.line, borderRadius: 9, overflow: "hidden" }}>
                <div style={{ width: `${(b.value / maxBar) * 100 * t}%`, height: "100%", background: toneColor(b.tone ?? "jev") }} />
              </div>
              <span style={{ width: 90, textAlign: "right", fontFamily: mono, fontSize: 22 }}>{fmt(Math.round(b.value * t))}</span>
            </div>
          ))}
        </div>
      ) : null}
    </Frame>
  );
};
