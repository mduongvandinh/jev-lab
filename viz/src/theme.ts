import { loadFont as loadSans } from "@remotion/google-fonts/BeVietnamPro";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

export const sans = loadSans("normal", { weights: ["400", "600", "800"], subsets: ["latin", "vietnamese"] }).fontFamily;
export const mono = loadMono("normal", { weights: ["400", "700"], subsets: ["latin"] }).fontFamily;

export const C = {
  bg: "#07090f",
  panel: "#121826",
  line: "#243048",
  text: "#eef2f8",
  muted: "#8a97ad",
  jev: "#7c5cff",
  good: "#3ddc97",
  bad: "#ff5c7a",
  warn: "#ffc857",
};

export const toneColor = (tone?: string) => (tone === "good" ? C.good : tone === "bad" ? C.bad : tone === "warn" ? C.warn : tone === "muted" ? C.muted : C.jev);

export const fmt = (n: number, digits = 0) => n.toLocaleString("vi-VN", { minimumFractionDigits: digits, maximumFractionDigits: digits });
