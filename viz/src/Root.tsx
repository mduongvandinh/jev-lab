import React from "react";
import { Composition } from "remotion";
import episodes from "./data/episodes.json";
import { Lab, totalFrames, Voice } from "./Lab";
import { Episode } from "./types";

type Entry = { readonly episode: Episode; readonly voice: Voice };
const ALL = episodes as unknown as Record<string, Entry>;

// Mỗi tập (episodes/<slug>/episode.json, gom bằng lab/publish.py) là một composition dọc 1080x1920
export const RemotionRoot: React.FC = () => (
  <>
    {Object.entries(ALL).map(([slug, { episode, voice }]) => (
      <Composition key={slug} id={`Lab-${slug}`} component={Lab} durationInFrames={totalFrames(episode, voice)} fps={30} width={1080} height={1920} defaultProps={{ episode, voice }} />
    ))}
  </>
);
