import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, sans } from "../theme";
import { RevealScene } from "../types";
import { rise, useAccent } from "../common";

// Kết quả: tiêu đề lớn, các con số chính, ý rút ra, và chú thích phạm vi dữ liệu
export const Reveal: React.FC<{ readonly s: RevealScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = useAccent();
  return (
    <AbsoluteFill style={{ padding: "140px 64px 560px", fontFamily: sans, color: C.text, gap: 22, background: `radial-gradient(circle at 85% 12%, ${accent}44, transparent 50%)` }}>
      <div style={{ fontSize: 26, fontWeight: 800, color: accent, letterSpacing: 2, ...rise(frame, fps) }}>{s.kicker}</div>
      <div style={{ fontSize: 76, fontWeight: 800, lineHeight: 1.05, ...rise(frame, fps, 6) }}>{s.headline}</div>
      <div style={{ fontSize: 34, lineHeight: 1.35, ...rise(frame, fps, 12) }}>{s.tagline}</div>
      <div style={{ display: "flex", gap: 14, ...rise(frame, fps, 18) }}>
        {s.stats.map((st) => (
          <div key={st.label} style={{ flex: 1, background: C.panel, borderRadius: 18, padding: "14px 16px", border: `1.5px solid ${accent}66` }}>
            <div style={{ fontSize: 42, fontWeight: 800, color: accent }}>{st.value}</div>
            <div style={{ fontSize: 20, color: C.muted, lineHeight: 1.25 }}>{st.label}</div>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {s.bullets.slice(0, 4).map((b, i) => (
          <div key={b} style={{ display: "flex", gap: 14, fontSize: 29, lineHeight: 1.3, ...rise(frame, fps, 28 + i * 8) }}>
            <span style={{ color: accent, fontWeight: 800 }}>◆</span>
            <span>{b}</span>
          </div>
        ))}
      </div>
      {s.grid ? (
        <div style={{ ...rise(frame, fps, 50) }}>
          {s.gridTitle ? <div style={{ fontSize: 24, fontWeight: 800, color: C.muted, marginBottom: 10 }}>{s.gridTitle}</div> : null}
          <div style={{ display: "grid", gridTemplateColumns: s.gridCols === 1 ? "1fr" : "1fr 1fr", gap: s.gridCols === 1 ? 8 : 10 }}>
            {s.grid.map((g) => (
              <div key={g.label} style={{ display: "flex", justifyContent: "space-between", background: C.panel, borderRadius: 12, padding: s.gridCols === 1 ? "6px 16px" : "8px 16px", fontSize: s.gridCols === 1 ? 25 : 26 }}>
                <span>{g.label}</span>
                <b style={{ color: accent }}>{g.value}</b>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      <div style={{ fontSize: 21, color: C.muted, lineHeight: 1.35, ...rise(frame, fps, 60) }}>{s.footnote}</div>
    </AbsoluteFill>
  );
};
