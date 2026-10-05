import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { AXIS_VI, C, mono, vi } from "../theme";
import { Candidate, VizData } from "../types";
import { Chip, Frame, pop } from "./common";

const Meter: React.FC<{ readonly label: string; readonly value: number; readonly text: string; readonly color: string; readonly t: number }> = ({ label, value, text, color, t }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
    <span style={{ width: 260, fontSize: 28, color: C.muted }}>{label}</span>
    <div style={{ flex: 1, height: 22, background: C.line, borderRadius: 11, overflow: "hidden" }}>
      <div style={{ width: `${Math.min(1, value) * 100 * t}%`, height: "100%", background: color }} />
    </div>
    <span style={{ width: 150, textAlign: "right", fontFamily: mono, fontSize: 26 }}>{text}</span>
  </div>
);

// Lướt qua các ứng viên: Jev chấm mạch lạc / mới lạ / giống trường phái nào; bị loại thì đóng dấu đỏ
export const Candidates: React.FC<{ readonly data: VizData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const list: readonly Candidate[] = data.candidates.slice(0, 10);
  const per = Math.floor(durationInFrames / list.length);
  const i = Math.min(list.length - 1, Math.floor(frame / per));
  const local = frame - i * per;
  const c = list[i];
  const t = interpolate(local, [4, per * 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const stamp = pop(frame, fps, i * per + per * 0.6);
  const passed = list.slice(0, i + (local > per * 0.6 ? 1 : 0)).filter((x) => x.pass).length;
  return (
    <Frame step="BƯỚC 4 · JEV CHẤM ỨNG VIÊN" title="Ghép mới có hợp lý không?" captionOff={`Ứng viên ${i + 1}/${list.length} · đã qua vòng: ${passed}`}>
      <div style={{ position: "absolute", top: 380, left: 56, right: 56, background: C.panel, borderRadius: 26, padding: 34, border: `2px solid ${C.line}`, display: "flex", flexDirection: "column", gap: 24 }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
          {Object.entries(c.combo).map(([ax, v]) => (
            <span key={ax} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              <span style={{ fontSize: 20, color: C.muted }}>{AXIS_VI[ax]}</span>
              <Chip text={vi(v)} size={28} />
            </span>
          ))}
        </div>
        <div style={{ fontFamily: mono, fontSize: 22, color: C.muted }}>có trong mẫu: 0 ảnh</div>
        <Meter label="Mạch lạc (Noul)" value={c.coherent} text={`${Math.round(c.coherent * 100)}%`} color={C.good} t={t} />
        <Meter label="Mới lạ (Score)" value={c.novelty / 4} text={`${c.novelty.toFixed(1)}/4`} color={C.jev} t={t} />
        <Meter label="Hợp mạng xã hội" value={c.appeal / 4} text={`${c.appeal.toFixed(1)}/4`} color={C.warn} t={t} />
        <div style={{ fontSize: 28 }}>
          Gần nhất: <b>{vi(c.closest)}</b> <span style={{ fontFamily: mono, color: C.muted }}>{Math.round(c.closestProb * 100)}%</span>
        </div>
      </div>
      <div
        style={{
          position: "absolute", top: 1060, left: 0, right: 0, textAlign: "center", opacity: stamp,
          transform: `scale(${interpolate(stamp, [0, 1], [1.6, 1])}) rotate(-6deg)`,
        }}
      >
        <span style={{ display: "inline-block", fontSize: 64, fontWeight: 800, letterSpacing: 4, padding: "8px 30px", borderRadius: 14, border: `6px solid ${c.pass ? C.good : C.bad}`, color: c.pass ? C.good : C.bad }}>
          {c.pass ? "QUA VÒNG" : "LOẠI"}
        </span>
      </div>
    </Frame>
  );
};
