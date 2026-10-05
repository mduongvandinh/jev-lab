import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Tile } from "../Tile";
import { C, mono } from "../theme";
import { Mode, VizData } from "../types";
import { Frame } from "./common";

const COLS = 5;
const W = 176;
const H = 236;
const GAP = 16;

// Bức tường ảnh cuộn nhanh: ảnh bị loại chỉ là ô khóa xám kèm lý do, không bao giờ hiện ảnh
export const Wall: React.FC<{ readonly data: VizData; readonly mode: Mode }> = ({ data, mode }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = interpolate(frame, [0, durationInFrames - 20], [0, 1], { extrapolateRight: "clamp" });
  const every = Math.max(4, Math.round(data.kept / Math.max(data.excluded.length, 1)));
  const columns = Array.from({ length: COLS }, (_, c) => {
    const items = data.tiles.filter((_, i) => i % COLS === c).slice(0, 26);
    return items.flatMap((t, i) => (i % every === every - 1 && data.excluded[(c * 7 + i) % data.excluded.length] ? [t, data.excluded[(c * 7 + i) % data.excluded.length]] : [t]));
  });
  const scanned = Math.round(progress * data.scanned);
  const excluded = Math.round(progress * data.excluded.length);
  return (
    <Frame step="BƯỚC 1 · THU THẬP & LỌC" title="Lướt qua từng ảnh" captionOff="Chỉ giữ ảnh an toàn, loại ảnh nhạy cảm và meme">
      <div style={{ position: "absolute", top: 380, left: 40, right: 40, height: 880, overflow: "hidden", display: "flex", gap: GAP, justifyContent: "center", maskImage: "linear-gradient(transparent, black 8%, black 92%, transparent)" }}>
        {columns.map((col, c) => {
          const speed = 9 + (c % 3) * 3;
          const y = -((frame * speed) % ((H + GAP) * 10)) - (c % 2) * 80;
          return (
            // Cột không bị kéo giãn theo khung (nếu không, ô ảnh trống nội dung sẽ bị co về 0px)
            <div key={c} style={{ display: "flex", flexDirection: "column", gap: GAP, alignSelf: "flex-start", transform: `translateY(${y}px)` }}>
              {col.map((item, i) =>
                "reason" in item ? (
                  <div key={`x${i}`} style={{ width: W, height: H, flexShrink: 0, borderRadius: 14, background: "#1b2130", border: `3px solid ${C.bad}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10, color: C.bad, textAlign: "center", padding: 12 }}>
                    <div style={{ fontSize: 56 }}>🔒</div>
                    <div style={{ fontSize: 22, fontWeight: 800 }}>LOẠI</div>
                    <div style={{ fontSize: 18, color: C.muted }}>{item.reason}</div>
                  </div>
                ) : (
                  <Tile key={item.id} tile={item} mode={mode} w={W} h={H} />
                ),
              )}
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: 315, left: 64, right: 64, display: "flex", justifyContent: "space-between", fontFamily: mono, fontSize: 32 }}>
        <span>đã quét <b style={{ color: C.text }}>{scanned.toLocaleString("vi-VN")}</b></span>
        <span style={{ color: C.bad }}>loại {excluded}</span>
      </div>
      {mode === "internal" ? (
        <div style={{ position: "absolute", top: 1270, left: 64, right: 64, fontSize: 22, color: C.muted }}>Ảnh từ cộng đồng Civitai, thuộc về các tác giả</div>
      ) : null}
    </Frame>
  );
};
