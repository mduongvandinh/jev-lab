import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Tile } from "../Tile";
import { AXIS_VI, C, mono, vi } from "../theme";
import { Mode, VizData } from "../types";
import { Chip, Frame, rise } from "./common";

const SHOWN = 6;

// Jev gắn nhãn: tia quét đi qua từng ảnh, nhãn + xác suất thật hiện ra; cột đếm theo trục lớn dần
export const Label: React.FC<{ readonly data: VizData; readonly mode: Mode }> = ({ data, mode }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const per = Math.floor((durationInFrames * 0.55) / SHOWN);
  const tiles = data.tiles.filter((t) => t.labels.medium && t.labels.medium[1] >= 0.8).slice(0, SHOWN);
  const grow = interpolate(frame, [0, durationInFrames - 30], [0.05, 1], { extrapolateRight: "clamp" });
  const tally = Object.entries(data.axisCounts.medium).filter(([k]) => k !== "unclear").sort((a, b) => b[1] - a[1]).slice(0, 5);
  const max = tally[0]?.[1] ?? 1;
  return (
    <Frame step="BƯỚC 2 · JEV GẮN NHÃN" title="Mỗi ảnh, 6 câu hỏi" captionOff={`Jev trả lời ${data.kept.toLocaleString("vi-VN")} ảnh, mỗi câu kèm xác suất`}>
      <div style={{ position: "absolute", top: 340, left: 48, right: 48, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
        {tiles.map((t, i) => {
          const start = i * per;
          const scan = interpolate(frame, [start, start + per * 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const done = frame > start + per * 0.6;
          return (
            <div key={t.id} style={{ display: "flex", gap: 14, alignItems: "center", background: C.panel, borderRadius: 18, padding: 12, border: `2px solid ${done ? C.jev : C.line}`, opacity: frame >= start ? 1 : 0.35 }}>
              <div style={{ position: "relative" }}>
                <Tile tile={t} mode={mode} w={150} h={190} credit />
                {frame >= start && !done && <div style={{ position: "absolute", left: 0, right: 0, top: `${scan * 100}%`, height: 6, background: C.jev, boxShadow: `0 0 18px ${C.jev}` }} />}
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, minWidth: 0 }}>
                {(["medium", "technique", "era"] as const).map((ax, k) =>
                  done && t.labels[ax] ? (
                    <div key={ax} style={{ ...rise(frame, fps, start + per * 0.6 + k * 3), display: "flex", flexDirection: "column", gap: 2 }}>
                      <span style={{ fontSize: 17, color: C.muted }}>{AXIS_VI[ax]}</span>
                      <span style={{ display: "flex", gap: 8, alignItems: "center" }}>
                        <Chip text={vi(t.labels[ax][0])} size={19} />
                        <span style={{ fontFamily: mono, fontSize: 18, color: C.good }}>{Math.round(t.labels[ax][1] * 100)}%</span>
                      </span>
                    </div>
                  ) : null,
                )}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: 1085, left: 64, right: 64 }}>
        <div style={{ fontSize: 26, fontWeight: 800, color: C.muted, marginBottom: 12 }}>Chất liệu phổ biến nhất</div>
        {tally.map(([k, n]) => (
          <div key={k} style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 10 }}>
            <span style={{ width: 230, fontSize: 26 }}>{vi(k)}</span>
            <div style={{ flex: 1, height: 26, background: C.line, borderRadius: 13, overflow: "hidden" }}>
              <div style={{ width: `${(n / max) * 100 * grow}%`, height: "100%", background: C.jev }} />
            </div>
            <span style={{ width: 70, textAlign: "right", fontFamily: mono, fontSize: 24 }}>{Math.round(n * grow)}</span>
          </div>
        ))}
      </div>
    </Frame>
  );
};
