import React from "react";
import { Composition } from "remotion";
import viz from "./data/viz.json";
import { StyleScan, TOTAL } from "./StyleScan";
import { VizData } from "./types";

const data = viz as unknown as VizData;

// Bản đăng dùng ảnh thật kèm ghi công tác giả; bản khối màu giữ làm phương án dự phòng
export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="StyleScan-dang" component={StyleScan} durationInFrames={TOTAL} fps={30} width={1080} height={1920} defaultProps={{ data, mode: "internal" as const }} />
    <Composition id="StyleScan-khoimau" component={StyleScan} durationInFrames={TOTAL} fps={30} width={1080} height={1920} defaultProps={{ data, mode: "public" as const }} />
  </>
);
