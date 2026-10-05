import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, mono, sans, toneColor } from "./theme";
import { Card } from "./types";

export const pop = (frame: number, fps: number, delay = 0) => spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 16 });
export const rise = (frame: number, fps: number, delay = 0) => {
  const p = pop(frame, fps, delay);
  return { opacity: p, transform: `translateY(${interpolate(p, [0, 1], [24, 0])}px)` };
};

export const AccentContext = React.createContext(C.jev);
export const useAccent = () => React.useContext(AccentContext);

// Tiêu đề cảnh (khung dọc 1080x1920): bước, tiêu đề, và huy hiệu kỹ thuật cookbook nếu cảnh minh họa một kỹ thuật
export const Frame: React.FC<{ readonly step?: string; readonly title?: string; readonly cookbook?: string; readonly children: React.ReactNode }> = ({ step, title, cookbook, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = useAccent();
  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: sans, color: C.text }}>
      <div style={{ position: "absolute", top: 140, left: 64, right: 64, ...rise(frame, fps) }}>
        {step ? <div style={{ fontSize: 26, fontWeight: 800, color: accent, letterSpacing: 2 }}>{step}</div> : null}
        {title ? <div style={{ fontSize: 56, fontWeight: 800, lineHeight: 1.12, marginTop: 6 }}>{title}</div> : null}
        {cookbook ? (
          <div style={{ marginTop: 12, display: "inline-flex", gap: 10, alignItems: "center", fontSize: 22, color: C.text, border: `1.5px solid ${accent}`, borderRadius: 999, padding: "5px 16px" }}>
            <span style={{ color: accent, fontWeight: 800 }}>Cookbook</span>
            <span>{cookbook}</span>
          </div>
        ) : null}
      </div>
      {children}
    </div>
  );
};

export const Chip: React.FC<{ readonly text: string; readonly color?: string; readonly size?: number }> = ({ text, color, size = 22 }) => {
  const accent = useAccent();
  return (
    <span style={{ display: "inline-block", fontSize: size, fontWeight: 700, color: "#fff", background: color ?? accent, borderRadius: 999, padding: "4px 12px", whiteSpace: "nowrap" }}>{text}</span>
  );
};

// Thẻ dữ liệu chung: biểu tượng hoặc ảnh, tiêu đề, dòng phụ; thẻ bị loại thành ô khóa, không lộ nội dung
export const CardView: React.FC<{ readonly card: Card; readonly w: number; readonly h: number; readonly compact?: boolean }> = ({ card, w, h, compact }) => {
  const color = toneColor(card.tone);
  if (card.locked) {
    return (
      <div style={{ width: w, height: h, flexShrink: 0, borderRadius: 16, background: C.panel, border: `2px solid ${C.bad}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8, padding: 10, textAlign: "center" }}>
        <div style={{ fontSize: 44 }}>🔒</div>
        <div style={{ fontSize: 22, fontWeight: 800, color: C.bad }}>LOẠI</div>
        <div style={{ fontSize: 17, color: C.muted, lineHeight: 1.25 }}>{card.locked}</div>
      </div>
    );
  }
  const side = Boolean(card.img) && w >= h * 1.6;
  return (
    <div style={{ width: w, height: h, flexShrink: 0, borderRadius: 16, overflow: "hidden", position: "relative", background: C.panel, border: `1.5px solid ${card.tone ? color : C.line}`, display: "flex", flexDirection: side ? "row" : "column" }}>
      {card.img ? (
        <Img src={staticFile(card.img)} style={side ? { width: h, height: h, objectFit: "cover", objectPosition: "center 20%", flexShrink: 0 } : { width: "100%", flex: 1, minHeight: 0, objectFit: card.fit ?? "cover", background: card.fit === "contain" ? "#fff" : undefined, padding: card.fit === "contain" ? 14 : 0 }} />
      ) : null}
      <div style={{ padding: compact ? "10px 12px" : "14px 16px", display: "flex", flexDirection: "column", gap: 4, flex: card.img && !side ? undefined : 1, minWidth: 0, justifyContent: side ? "flex-start" : card.img ? undefined : "center", overflow: "hidden" }}>
        {card.icon ? <div style={{ fontSize: compact ? 40 : 52, lineHeight: 1.1 }}>{card.icon}</div> : null}
        <div style={{ fontSize: compact ? (card.img ? 17 : 20) : 24, fontWeight: 800, lineHeight: 1.35, paddingTop: 2, flexShrink: 0, overflow: "hidden", display: "-webkit-box", WebkitLineClamp: card.img && !side ? 1 : 2, WebkitBoxOrient: "vertical" }}>{card.title}</div>
        {card.sub ? <div style={{ fontSize: compact ? 16 : 19, color: C.muted, lineHeight: 1.25 }}>{card.sub}</div> : null}
        {card.img && card.credit ? <div style={{ fontSize: compact ? 13 : 16, color: C.muted, lineHeight: 1.2, ...(side ? {} : { whiteSpace: "nowrap" as const, overflow: "hidden", textOverflow: "ellipsis" }) }}>{card.credit}</div> : null}
        {(card.lines ?? []).map((l) => (
          <div key={l} style={{ fontFamily: mono, fontSize: compact ? 15 : 18, color: C.text, lineHeight: 1.3 }}>{l}</div>
        ))}
      </div>
      {card.credit && !card.img ? (
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "3px 8px", background: "rgba(0,0,0,0.6)", fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{card.credit}</div>
      ) : null}
    </div>
  );
};

export const Meter: React.FC<{ readonly label: string; readonly value: number; readonly text: string; readonly color: string; readonly t: number; readonly labelW?: number }> = ({ label, value, text, color, t, labelW = 280 }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
    <span style={{ width: labelW, fontSize: 27, color: C.muted, lineHeight: 1.2 }}>{label}</span>
    <div style={{ flex: 1, height: 22, background: C.line, borderRadius: 11, overflow: "hidden" }}>
      <div style={{ width: `${Math.max(0, Math.min(1, value)) * 100 * t}%`, height: "100%", background: color }} />
    </div>
    <span style={{ minWidth: 130, textAlign: "right", fontFamily: mono, fontSize: 25 }}>{text}</span>
  </div>
);
