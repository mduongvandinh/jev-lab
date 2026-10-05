import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, fmt, mono } from "../theme";
import { ScanScene } from "../types";
import { CardView, Frame } from "../common";

const GAP = 16;

// Bức tường dữ liệu cuộn dọc nhiều cột, bộ đếm chạy theo thời gian
export const Scan: React.FC<{ readonly s: ScanScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const cols = s.cols ?? 4;
  const W = Math.floor((1000 - GAP * (cols - 1)) / cols);
  const H = s.cardH ?? 220;
  const columns = Array.from({ length: cols }, (_, c) => s.cards.filter((_, i) => i % cols === c));
  const p = interpolate(frame, [0, durationInFrames - 20], [0, 1], { extrapolateRight: "clamp" });
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top: s.cookbook ? 360 : 315, left: 64, right: 64, display: "flex", justifyContent: "space-between", fontFamily: mono, fontSize: 30 }}>
        <span>{s.totalLabel} <b>{fmt(Math.round(s.total * p))}</b> {s.unit ?? ""}</span>
        {s.excluded !== undefined ? <span style={{ color: C.bad }}>{s.excludedLabel} {fmt(Math.round(s.excluded * p))}</span> : null}
      </div>
      {s.credit ? <div style={{ position: "absolute", top: (s.cookbook ? 360 : 315) + 46, left: 64, right: 64, fontSize: 20, color: C.muted, lineHeight: 1.3 }}>{s.credit}</div> : null}
      <div style={{ position: "absolute", top: (s.cookbook ? 420 : 380) + (s.credit ? 60 : 0), left: 40, right: 40, height: (s.cookbook ? 840 : 880) - (s.credit ? 60 : 0), overflow: "hidden", display: "flex", gap: GAP, maskImage: "linear-gradient(transparent, #000 6%, #000 90%, transparent)" }}>
        {columns.map((col, c) => {
          const span = Math.max(1, col.length - 4) * (H + GAP);
          const speed = 7 + (c % 3) * 2.5;
          const y = -((frame * speed + (c % 2) * 90) % span);
          return (
            <div key={c} style={{ display: "flex", flexDirection: "column", gap: GAP, alignSelf: "flex-start", transform: `translateY(${y}px)` }}>
              {col.map((card, i) => (
                <CardView key={i} card={card} w={W} h={H} compact />
              ))}
            </div>
          );
        })}
      </div>

    </Frame>
  );
};
