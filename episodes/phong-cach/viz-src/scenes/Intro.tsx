import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, mono, sans } from "../theme";
import { VizData } from "../types";
import { rise } from "./common";

export const Intro: React.FC<{ readonly data: VizData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ justifyContent: "center", padding: "0 72px 360px", fontFamily: sans, color: C.text, gap: 28 }}>
      <div style={{ fontSize: 30, fontWeight: 800, color: C.jev, letterSpacing: 3, ...rise(frame, fps) }}>THÍ NGHIỆM VỚI JEV</div>
      <div style={{ fontSize: 96, fontWeight: 800, lineHeight: 1.05, ...rise(frame, fps, 6) }}>Đi tìm phong cách chưa ai vẽ</div>
      <div style={{ fontSize: 40, color: C.muted, lineHeight: 1.35, ...rise(frame, fps, 14) }}>
        {data.scanned.toLocaleString("vi-VN")} ảnh từ {data.source}, Jev chấm từng ảnh rồi tìm khoảng trống
      </div>
      <div style={{ fontFamily: mono, fontSize: 26, color: C.muted, ...rise(frame, fps, 22) }}>fb.com/m.duongvandinh</div>
    </AbsoluteFill>
  );
};
