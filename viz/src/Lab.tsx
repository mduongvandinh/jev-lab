import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, Series, staticFile } from "remotion";
import { AccentContext } from "./common";
import { Bars } from "./scenes/Bars";
import { Heat } from "./scenes/Heat";
import { Intro } from "./scenes/Intro";
import { Judge } from "./scenes/Judge";
import { Columns } from "./scenes/Columns";
import { Label } from "./scenes/Label";
import { Timeline } from "./scenes/Timeline";
import { Pitch } from "./scenes/Pitch";
import { Repeat } from "./scenes/Repeat";
import { Reveal } from "./scenes/Reveal";
import { Scan } from "./scenes/Scan";
import { Technique } from "./scenes/Technique";
import { Caption, LEAD, Subtitles } from "./Subtitles";
import { C } from "./theme";
import { Episode, Scene } from "./types";

export type Voice = Record<string, { readonly audio: string; readonly seconds: number; readonly captions: readonly Caption[] }>;

// Thời lượng tối thiểu theo kiểu cảnh (frame); cảnh tự dài thêm cho vừa giọng đọc
const BASE: Record<Scene["type"], number> = { intro: 90, scan: 300, technique: 360, label: 390, heat: 330, bars: 300, repeat: 300, judge: 400, reveal: 420, pitch: 330, timeline: 420, columns: 360 };
export const sceneFrames = (s: Scene, voice: Voice) => Math.max(BASE[s.type], LEAD + Math.ceil((voice[s.key]?.seconds ?? 0) * 30) + 30);
export const totalFrames = (ep: Episode, voice: Voice) => ep.scenes.reduce((a, s) => a + sceneFrames(s, voice), 0);

const Body: React.FC<{ readonly s: Scene }> = ({ s }) => {
  switch (s.type) {
    case "intro": return <Intro s={s} />;
    case "scan": return <Scan s={s} />;
    case "technique": return <Technique s={s} />;
    case "label": return <Label s={s} />;
    case "heat": return <Heat s={s} />;
    case "bars": return <Bars s={s} />;
    case "repeat": return <Repeat s={s} />;
    case "judge": return <Judge s={s} />;
    case "reveal": return <Reveal s={s} />;
    case "pitch": return <Pitch s={s} />;
    case "timeline": return <Timeline s={s} />;
    case "columns": return <Columns s={s} />;
  }
};

export const Lab: React.FC<{ readonly episode: Episode; readonly voice: Voice }> = ({ episode, voice }) => (
  <AccentContext.Provider value={episode.accent ?? C.jev}>
    <AbsoluteFill style={{ background: C.bg }}>
      <Series>
        {episode.scenes.map((s) => (
          <Series.Sequence key={s.key} durationInFrames={sceneFrames(s, voice)} name={s.key}>
            <Body s={s} />
            {voice[s.key] ? (
              <>
                <Sequence from={LEAD} layout="none">
                  <Audio src={staticFile(voice[s.key].audio)} />
                </Sequence>
                <Subtitles captions={voice[s.key].captions} />
              </>
            ) : null}
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  </AccentContext.Provider>
);
