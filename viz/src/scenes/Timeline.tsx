import React from "react";
import { Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, mono } from "../theme";
import { TimelineScene } from "../types";
import { Frame, rise, useAccent } from "../common";

// Dòng thời gian dọc: mỗi mốc một hàng (ảnh, năm, tên, số liệu), hiện lần lượt theo nhịp cảnh
export const Timeline: React.FC<{ readonly s: TimelineScene }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const accent = useAccent();
  const step = Math.floor((durationInFrames * 0.75) / s.items.length);
  const rowH = Math.min(150, Math.floor(880 / s.items.length) - 10);
  return (
    <Frame step={s.step} title={s.title} cookbook={s.cookbook}>
      <div style={{ position: "absolute", top: s.cookbook ? 400 : 350, left: 48, right: 48, display: "flex", flexDirection: "column", gap: 10 }}>
        {s.items.map((it, i) => (
          <div key={it.years + it.title} style={{ display: "flex", gap: 16, height: rowH, background: C.panel, borderRadius: 18, overflow: "hidden", borderLeft: `8px solid ${it.color ?? accent}`, ...rise(frame, fps, 8 + i * step) }}>
            {it.img ? <Img src={staticFile(it.img)} style={{ width: rowH, height: rowH, objectFit: "cover", objectPosition: "center 20%", flexShrink: 0 }} /> : null}
            <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", gap: 2, padding: "6px 4px", minWidth: 0 }}>
              <div style={{ fontFamily: mono, fontSize: 21, color: it.color ?? accent }}>{it.years}</div>
              <div style={{ fontSize: 31, fontWeight: 800, lineHeight: 1.15 }}>{it.title}</div>
              {it.sub ? <div style={{ fontSize: 21, color: C.muted, lineHeight: 1.25 }}>{it.sub}</div> : null}
              {it.credit ? <div style={{ fontSize: 13, color: C.muted, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{it.credit}</div> : null}
            </div>
            {it.stat ? <div style={{ alignSelf: "center", paddingRight: 20, fontSize: 30, fontWeight: 800, textAlign: "right", whiteSpace: "pre-line", lineHeight: 1.15 }}>{it.stat}</div> : null}
          </div>
        ))}
      </div>
    </Frame>
  );
};
