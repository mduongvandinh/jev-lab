import React from "react";
import { Img, staticFile } from "remotion";
import { Mode, Tile as TileT } from "./types";

const hexToHsl = (h: string) => {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
  const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2;
  const s = max === min ? 0 : (max - min) / (1 - Math.abs(2 * l - 1));
  return { s, l };
};

// Màu đại diện: ưu tiên màu tươi và đủ sáng (ảnh tối thì màu chiếm nhiều nhất thường gần đen, khó thấy trên nền video)
const vivid = (palette: readonly string[]) =>
  [...palette].sort((x, y) => {
    const a = hexToHsl(x), b = hexToHsl(y);
    return b.s * (1 - Math.abs(b.l - 0.55)) - a.s * (1 - Math.abs(a.l - 0.55));
  });

// Ô ảnh: bản nội bộ hiện ảnh thật; bản đăng thay bằng khối màu từ bảng màu (không đăng lại tác phẩm của người khác)
export const Tile: React.FC<{ readonly tile: TileT; readonly mode: Mode; readonly w: number; readonly h: number; readonly credit?: boolean; readonly style?: React.CSSProperties }> = ({
  tile,
  mode,
  w,
  h,
  credit = false,
  style,
}) => {
  const [a, b, c] = vivid(tile.palette.length ? tile.palette : ["#555"]);
  return (
    <div style={{ width: w, height: h, flexShrink: 0, borderRadius: 14, overflow: "hidden", position: "relative", background: "#1a2030", border: "1px solid rgba(255,255,255,0.12)", ...style }}>
      {mode === "internal" ? (
        <>
          <Img src={staticFile(`thumbs/${tile.id}.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          {credit && tile.author ? (
            // Ghi công tác giả ảnh (Civitai)
            <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "3px 6px", background: "rgba(0,0,0,0.6)", color: "#fff", fontSize: 13, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              @{tile.author}
            </div>
          ) : null}
        </>
      ) : (
        <div style={{ width: "100%", height: "100%", background: `linear-gradient(150deg, ${a} 0%, ${b ?? a} 55%, ${c ?? b ?? a} 100%)` }} />
      )}
    </div>
  );
};
