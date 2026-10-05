import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, Series, staticFile } from "remotion";
import narration from "./data/narration.json";
import { Candidates } from "./scenes/Candidates";
import { Heat } from "./scenes/Heat";
import { Intro } from "./scenes/Intro";
import { Label } from "./scenes/Label";
import { Reveal } from "./scenes/Reveal";
import { Wall } from "./scenes/Wall";
import { Caption, LEAD, Subtitles } from "./Subtitles";
import { C } from "./theme";
import { Mode, VizData } from "./types";

type Narr = Record<string, { readonly audio: string; readonly seconds: number; readonly captions: readonly Caption[] }>;
const N = narration as unknown as Narr;

// Thời lượng tối thiểu của từng cảnh (frame); cảnh tự dài thêm cho vừa giọng đọc
const BASE = { intro: 90, wall: 300, label: 390, heat: 330, candidates: 420, reveal: 420 } as const;
export const durationOf = (scene: keyof typeof BASE) => Math.max(BASE[scene], LEAD + Math.ceil((N[scene]?.seconds ?? 0) * 30) + 30);
export const TOTAL = (Object.keys(BASE) as (keyof typeof BASE)[]).reduce((a, s) => a + durationOf(s), 0);

const Voice: React.FC<{ readonly scene: string }> = ({ scene }) =>
  N[scene] ? (
    <>
      <Sequence from={LEAD} layout="none">
        <Audio src={staticFile(N[scene].audio)} />
      </Sequence>
      <Subtitles captions={N[scene].captions} />
    </>
  ) : null;

export const StyleScan: React.FC<{ readonly data: VizData; readonly mode: Mode }> = ({ data, mode }) => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Series>
      <Series.Sequence durationInFrames={durationOf("intro")} name="Mở đầu"><Intro data={data} /><Voice scene="intro" /></Series.Sequence>
      <Series.Sequence durationInFrames={durationOf("wall")} name="Lướt & lọc"><Wall data={data} mode={mode} /><Voice scene="wall" /></Series.Sequence>
      <Series.Sequence durationInFrames={durationOf("label")} name="Jev gắn nhãn"><Label data={data} mode={mode} /><Voice scene="label" /></Series.Sequence>
      <Series.Sequence durationInFrames={durationOf("heat")} name="Bản đồ"><Heat data={data} /><Voice scene="heat" /></Series.Sequence>
      <Series.Sequence durationInFrames={durationOf("candidates")} name="Ứng viên"><Candidates data={data} /><Voice scene="candidates" /></Series.Sequence>
      <Series.Sequence durationInFrames={durationOf("reveal")} name="Lộ diện"><Reveal data={data} /><Voice scene="reveal" /></Series.Sequence>
    </Series>
  </AbsoluteFill>
);
