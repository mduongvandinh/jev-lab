import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, mono } from "../theme";
import { ColumnsScene } from "../types";
import { Frame, useAccent } from "../common";

// Biểu đồ cột theo thời gian: cột mọc lần lượt từ trái sang phải, cột nổi bật có nhãn số
export const Columns: React.FC<{ readonly s: ColumnsScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const accent = useAccent();
  const max = Math.max(...s.cols.map((c) => c.value));
  const H = 620;
  const W = 1000;
  const cw = W / s.cols.length;
  const top = s.cookbook ? 420 : 380;
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top, left: 40, width: W, height: H + 70 }}>
        {s.cols.map((c, i) => {
          const t = interpolate(frame, [10 + i * ((durationInFrames * 0.5) / s.cols.length), 30 + i * ((durationInFrames * 0.5) / s.cols.length)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const h = (c.value / max) * H * t;
          return (
            <div key={c.label + i} style={{ position: "absolute", left: i * cw, width: cw, bottom: 70, height: H, display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center" }}>
              {c.highlight || i === s.cols.length - 1 ? <div style={{ fontFamily: mono, fontSize: 20, color: C.text, opacity: t, marginBottom: 4 }}>{Math.round(c.value * t)}</div> : null}
              <div style={{ width: cw - 6, height: h, background: c.color ?? accent, borderRadius: "6px 6px 0 0", boxShadow: c.highlight ? `0 0 14px ${C.warn}` : "none", border: c.highlight ? `2px solid ${C.warn}` : "none" }} />
              <div style={{ position: "absolute", bottom: -34, fontFamily: mono, fontSize: 16, color: c.highlight ? C.warn : C.muted, whiteSpace: "nowrap" }}>{c.label}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: top + H + 90, left: 64, right: 64, display: "flex", flexWrap: "wrap", gap: 14 }}>
        {(s.legend ?? []).map((l) => (
          <span key={l.label} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 22 }}>
            <span style={{ width: 18, height: 18, borderRadius: 4, background: l.color }} />
            {l.label}
          </span>
        ))}
      </div>
      {s.note ? <div style={{ position: "absolute", top: top + H + 140, left: 64, right: 64, fontSize: 22, color: C.muted }}>{s.note}</div> : null}
    </Frame>
  );
};
