import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, mono, vi } from "../theme";
import { VizData } from "../types";
import { Frame } from "./common";

// Bản đồ nhiệt Chất liệu × Kỹ thuật lấp dần; ô trống (0 ảnh) sáng viền vàng: "chưa ai làm"
export const Heat: React.FC<{ readonly data: VizData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const { rows, cols, counts } = data.heat;
  const max = Math.max(1, ...counts.flat());
  const total = rows.length * cols.length;
  const filled = interpolate(frame, [10, durationInFrames * 0.55], [0, total], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const glow = frame > durationInFrames * 0.6;
  const cell = Math.floor(760 / cols.length);
  const empty = counts.flat().filter((n) => n === 0).length;
  return (
    <Frame step="BƯỚC 3 · BẢN ĐỒ PHONG CÁCH" title="Chỗ nào chưa ai làm?" captionOff={glow ? `${empty} ô trống: tổ hợp chưa xuất hiện trong ${data.kept} ảnh` : "Mỗi ô: số ảnh có cặp chất liệu × kỹ thuật đó"}>
      <div style={{ position: "absolute", top: 360, left: 40 }}>
        <div style={{ display: "flex", marginLeft: 210, height: 150, alignItems: "flex-end" }}>
          {cols.map((c) => (
            <div key={c} style={{ width: cell, display: "flex", justifyContent: "center" }}>
              <div style={{ transform: "rotate(-55deg)", transformOrigin: "bottom left", whiteSpace: "nowrap", fontSize: 20, color: C.muted, width: 20 }}>{vi(c)}</div>
            </div>
          ))}
        </div>
        {rows.map((r, i) => (
          <div key={r} style={{ display: "flex", alignItems: "center" }}>
            <div style={{ width: 210, fontSize: 21, color: C.muted, textAlign: "right", paddingRight: 12 }}>{vi(r)}</div>
            {cols.map((c, j) => {
              const idx = i * cols.length + j;
              const n = counts[i][j];
              const shown = idx < filled;
              const isEmpty = shown && n === 0;
              return (
                <div
                  key={c}
                  style={{
                    width: cell - 6, height: cell - 6, margin: 3, borderRadius: 8,
                    background: shown && n > 0 ? `rgba(124,92,255,${0.18 + 0.82 * (n / max)})` : "transparent",
                    border: isEmpty ? `2px ${glow ? "solid" : "dashed"} ${glow ? C.warn : C.line}` : `1px solid ${C.line}`,
                    boxShadow: isEmpty && glow ? `0 0 ${10 + 8 * Math.sin(frame / 5)}px ${C.warn}` : "none",
                    display: "flex", alignItems: "center", justifyContent: "center", fontFamily: mono, fontSize: 18,
                    color: isEmpty ? C.warn : "#fff",
                  }}
                >
                  {shown ? (n > 0 ? n : glow ? "?" : "") : ""}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </Frame>
  );
};
