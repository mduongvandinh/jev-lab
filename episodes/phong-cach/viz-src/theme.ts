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

// Tên hiển thị tiếng Việt cho nhãn Jev
export const LABEL_VI: Record<string, string> = {
  watercolor: "Màu nước", oil_acrylic: "Sơn dầu/acrylic", ink_pen: "Mực/bút", pencil_charcoal: "Chì/than",
  digital_painting: "Vẽ số", vector_flat: "Vector phẳng", pixel: "Pixel", render_3d: "Dựng 3D", photo_manip: "Ảnh ghép",
  collage_mixed: "Cắt dán", craft_physical: "Thủ công", painterly: "Nét cọ", linework: "Nét vẽ", flat_shapes: "Mảng phẳng",
  realistic_detail: "Chi tiết thực", geometric: "Hình học", print_texture: "Vân in", glitch_distort: "Nhiễu glitch",
  ornamental: "Hoa văn", monochrome: "Đơn sắc", pastel: "Pastel", earthy_muted: "Màu đất", neon_saturated: "Neon",
  warm_dominant: "Tông ấm", cool_dominant: "Tông lạnh", high_contrast: "Tương phản", none: "Không trường phái",
  nouveau_deco: "Nouveau/Deco", east_asian_trad: "Á Đông cổ", retro_80s_90s: "Retro 80-90", medieval_gothic: "Trung cổ",
  scifi_futurist: "Viễn tưởng", folk_naive: "Dân gian", modernist_abstract: "Hiện đại trừu tượng", impressionist: "Ấn tượng",
  character_portrait: "Nhân vật", creature_fantasy: "Sinh vật", landscape_nature: "Phong cảnh", city_architecture: "Đô thị",
  object_still_life: "Đồ vật", abstract_pattern: "Trừu tượng", scene_narrative: "Cảnh kể chuyện", machine_vehicle: "Máy móc",
  serene: "Yên bình", melancholic: "U buồn", eerie_dark: "U tối", playful: "Vui nhộn", dramatic_epic: "Kịch tính",
  energetic_chaotic: "Sôi động", unclear: "Chưa rõ", none_fits: "Không giống ai",
};
export const vi = (k: string) => LABEL_VI[k] ?? k;

export const AXIS_VI: Record<string, string> = {
  medium: "Chất liệu", technique: "Kỹ thuật", palette: "Bảng màu", subject: "Chủ đề", mood: "Cảm xúc", era: "Trường phái",
};
