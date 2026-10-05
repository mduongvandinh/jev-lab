import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";
import { PitchScene } from "../types";
import { Frame, useAccent } from "../common";

// Nửa sân dọc, khung thành ở trên. Mỗi chấm một cú sút: to và sáng theo xác suất Jev; bàn thắng có viền trắng (hiện ở nửa sau cảnh)
const S = 12.5; // px mỗi yard
const W = 80 * S;
const H = 50 * S; // từ vạch giữa sân + 10 yard tới khung thành
const X0 = 70; // chỉ vẽ x >= 70

export const Pitch: React.FC<{ readonly s: PitchScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const accent = useAccent();
  const shown = Math.floor(interpolate(frame, [10, durationInFrames * 0.45], [0, s.points.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const goals = frame > durationInFrames * 0.55;
  const px = (y: number) => y * S;
  const py = (x: number) => (120 - x) * S;
  const line = { position: "absolute" as const, border: `2px solid ${C.line}` };
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top: s.cookbook ? 410 : 370, left: 40, width: W, height: H, background: "#0d1a12", borderRadius: 12, overflow: "hidden" }}>
        <div style={{ ...line, left: px(18), top: 0, width: px(44), height: 18 * S }} />
        <div style={{ ...line, left: px(30), top: 0, width: px(20), height: 6 * S }} />
        <div style={{ position: "absolute", left: px(36), top: 0, width: px(8), height: 8, background: "#fff" }} />
        <div style={{ position: "absolute", left: px(40) - 4, top: py(108) - 4, width: 8, height: 8, borderRadius: 4, background: C.line }} />
        {s.points.slice(0, shown).map((p, i) =>
          p.x < X0 ? null : (
            <div
              key={i}
              style={{
                position: "absolute", left: px(p.y) - (5 + p.p * 16) / 2, top: py(p.x) - (5 + p.p * 16) / 2, width: 5 + p.p * 16, height: 5 + p.p * 16, borderRadius: "50%",
                background: accent, opacity: 0.25 + p.p * 0.75, border: goals && p.g ? "2.5px solid #fff" : "none", boxShadow: goals && p.g ? "0 0 8px #fff" : "none",
              }}
            />
          ),
        )}
      </div>
      <div style={{ position: "absolute", top: (s.cookbook ? 410 : 370) + H + 14, left: 64, right: 64, fontSize: 23, color: C.muted, lineHeight: 1.35 }}>{s.legend}</div>
    </Frame>
  );
};
