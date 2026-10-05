import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, fmt, mono } from "../theme";
import { RepeatScene } from "../types";
import { Frame, pop, rise, useAccent } from "../common";

const W = 860;

const Track: React.FC<{ readonly values: readonly number[]; readonly lo: number; readonly hi: number; readonly delay: number; readonly zoom?: boolean }> = ({ values, lo, hi, delay, zoom }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = useAccent();
  return (
    <div style={{ position: "relative", width: W, height: zoom ? 46 : 34, background: zoom ? "#0b101b" : C.panel, borderRadius: 23, border: `1px solid ${zoom ? accent : C.line}` }}>
      <span style={{ position: "absolute", left: 0, top: zoom ? 50 : 38, fontFamily: mono, fontSize: 17, color: C.muted }}>{fmt(lo, zoom ? 2 : 0)}</span>
      <span style={{ position: "absolute", right: 0, top: zoom ? 50 : 38, fontFamily: mono, fontSize: 17, color: C.muted }}>{fmt(hi, zoom ? 2 : 0)}</span>
      {values.map((v, i) => {
        const p = pop(frame, fps, delay + i * 3);
        const x = 20 + ((v - lo) / (hi - lo)) * (W - 40);
        return <div key={i} style={{ position: "absolute", left: x - 8, top: zoom ? 15 : 9, width: 16, height: 16, borderRadius: 8, background: accent, opacity: (zoom ? 0.55 : 0.35) * p, transform: `scale(${p})` }} />;
      })}
    </div>
  );
};

// Self-consistency: hỏi lại cùng một câu nhiều lần, mỗi lần một chấm. Thang đầy đủ + thanh phóng to để thấy độ chụm
export const Repeat: React.FC<{ readonly s: RepeatScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top: s.cookbook ? 410 : 360, left: 64, right: 64, display: "flex", flexDirection: "column", gap: 52 }}>
        {s.rows.map((r, ri) => (
          <div key={r.label} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 26 }}>
              <span>{r.label}</span>
              <span style={{ fontFamily: mono, color: C.good, ...rise(frame, fps, 30 + ri * 20 + r.values.length * 3) }}>{r.text}</span>
            </div>
            <Track values={r.values} lo={r.min} hi={r.max} delay={10 + ri * 20} />
            {r.zoom ? (
              <div style={{ marginTop: 26 }}>
                <Track values={r.values} lo={r.zoom[0]} hi={r.zoom[1]} delay={14 + ri * 20} zoom />
              </div>
            ) : null}
          </div>
        ))}
        <div style={{ marginTop: 26, fontSize: 30, lineHeight: 1.35, ...rise(frame, fps, 60) }}>{s.verdict}</div>
      </div>
    </Frame>
  );
};
