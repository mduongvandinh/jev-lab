import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, mono, toneColor } from "../theme";
import { TechniqueScene } from "../types";
import { Chip, Frame, rise, useAccent } from "../common";

const KIND_COLOR: Record<string, string> = { Noul: "#3ddc97", Choice: "#7c5cff", Score: "#ffc857" };

// Minh họa một request Jev: dữ liệu (state) + các câu hỏi gộp một lần gọi -> từng đáp án theo tên
export const Technique: React.FC<{ readonly s: TechniqueScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const accent = useAccent();
  const qStart = 20;
  const qStep = Math.min(18, Math.floor((durationInFrames * 0.45) / Math.max(1, s.questions.length)));
  const rStart = qStart + qStep * s.questions.length + 15;
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top: 400, left: 56, right: 56, display: "flex", flexDirection: "column", gap: 18 }}>
        <div style={{ fontSize: 28, lineHeight: 1.3, ...rise(frame, fps, 4) }}>{s.idea}</div>
        <div style={{ border: `2px solid ${accent}`, borderRadius: 22, padding: 22, background: C.panel, display: "flex", flexDirection: "column", gap: 12, ...rise(frame, fps, 10) }}>
          <div style={{ fontSize: 20, color: accent, fontWeight: 800, letterSpacing: 2 }}>1 REQUEST</div>
          <div style={{ fontFamily: mono, fontSize: 19, color: C.muted, lineHeight: 1.4, background: "#0b101b", borderRadius: 12, padding: "10px 14px" }}>
            {s.stateLines.map((l) => (
              <div key={l}>{l}</div>
            ))}
          </div>
          {s.questions.map((q, i) => (
            <div key={q.name} style={{ display: "flex", alignItems: "center", gap: 12, ...rise(frame, fps, qStart + i * qStep) }}>
              <Chip text={q.kind} color={KIND_COLOR[q.kind]} size={20} />
              <span style={{ fontFamily: mono, fontSize: 21, color: C.muted }}>{q.name}</span>
              <span style={{ fontSize: 24 }}>{q.text}</span>
            </div>
          ))}
        </div>
        <div style={{ textAlign: "center", fontSize: 30, lineHeight: 1, color: accent, ...rise(frame, fps, rStart - 6) }}>↓</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
          {s.results.map((r, i) => (
            <div key={r.name} style={{ flex: s.results.length > 4 ? "1 1 30%" : "1 1 45%", background: C.panel, borderRadius: 16, padding: "10px 14px", border: `1.5px solid ${toneColor(r.tone)}`, ...rise(frame, fps, rStart + i * 6) }}>
              <div style={{ fontFamily: mono, fontSize: 19, color: C.muted }}>{r.name}</div>
              <div style={{ fontSize: s.results.length > 4 ? 25 : 30, fontWeight: 800, color: toneColor(r.tone) }}>{r.value}</div>
            </div>
          ))}
        </div>
        {s.footer ? <div style={{ fontSize: 24, color: C.muted, ...rise(frame, fps, rStart + 20) }}>{s.footer}</div> : null}
      </div>
    </Frame>
  );
};
