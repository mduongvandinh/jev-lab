// Khuôn dữ liệu chung cho mọi tập Jev Lab: mỗi tập là một danh sách cảnh, mỗi cảnh một kiểu dựng sẵn
export type Tone = "good" | "bad" | "warn" | "jev" | "muted";

export type Card = {
  readonly title: string;
  readonly sub?: string;
  readonly lines?: readonly string[];
  readonly icon?: string; // emoji
  readonly img?: string; // đường dẫn trong public/
  readonly fit?: "cover" | "contain"; // contain: logo, không cắt
  readonly credit?: string; // ghi công tác giả / nguồn
  readonly tone?: Tone;
  readonly locked?: string; // lý do loại: ô khóa, không hiện nội dung
};

type Base = { readonly key: string; readonly step?: string; readonly title?: string; readonly cookbook?: string };

export type IntroScene = Base & { readonly type: "intro"; readonly kicker: string; readonly headline: string; readonly sub: string };
export type ScanScene = Base & {
  readonly type: "scan";
  readonly cards: readonly Card[];
  readonly total: number;
  readonly totalLabel: string;
  readonly unit?: string;
  readonly excluded?: number;
  readonly excludedLabel?: string;
  readonly cols?: number;
  readonly cardH?: number;
  readonly credit?: string;
};
export type TechniqueScene = Base & {
  readonly type: "technique";
  readonly idea: string;
  readonly stateLines: readonly string[];
  readonly questions: readonly { readonly name: string; readonly kind: string; readonly text: string }[];
  readonly results: readonly { readonly name: string; readonly value: string; readonly tone?: Tone }[];
  readonly footer?: string;
};
export type Answer = { readonly q: string; readonly text: string; readonly prob?: number; readonly tone?: Tone };
export type LabelScene = Base & {
  readonly type: "label";
  readonly examples: readonly { readonly card: Card; readonly answers: readonly Answer[] }[];
  readonly tally?: { readonly title: string; readonly bars: readonly { readonly label: string; readonly value: number; readonly tone?: Tone }[] };
};
export type HeatScene = Base & {
  readonly type: "heat";
  readonly rows: readonly string[];
  readonly cols: readonly string[];
  readonly values: readonly (readonly number[])[];
  readonly digits?: number;
  readonly highlight?: readonly (readonly [number, number])[];
  readonly legend: string;
};
export type BarsScene = Base & {
  readonly type: "bars";
  readonly bars: readonly { readonly label: string; readonly value: number; readonly text: string; readonly tone?: Tone; readonly sub?: string }[];
  readonly note?: string;
};
export type RepeatScene = Base & {
  readonly type: "repeat";
  readonly rows: readonly { readonly label: string; readonly values: readonly number[]; readonly min: number; readonly max: number; readonly text: string; readonly zoom?: readonly [number, number] }[];
  readonly verdict: string;
};
export type JudgeScene = Base & {
  readonly type: "judge";
  readonly items: readonly {
    readonly card: Card;
    readonly metrics: readonly { readonly label: string; readonly value: number; readonly text: string; readonly tone?: Tone }[];
    readonly pass: boolean;
    readonly stamp: string;
  }[];
};
export type RevealScene = Base & {
  readonly type: "reveal";
  readonly kicker: string;
  readonly headline: string;
  readonly tagline: string;
  readonly stats: readonly { readonly value: string; readonly label: string }[];
  readonly bullets: readonly string[];
  readonly grid?: readonly { readonly label: string; readonly value: string }[];
  readonly gridTitle?: string;
  readonly gridCols?: number;
  readonly footnote: string;
};

export type PitchScene = Base & {
  readonly type: "pitch";
  readonly points: readonly { readonly x: number; readonly y: number; readonly p: number; readonly g: boolean }[]; // tọa độ StatsBomb (sân 120x80 yard)
  readonly legend: string;
};

export type TimelineScene = Base & {
  readonly type: "timeline";
  readonly items: readonly { readonly years: string; readonly title: string; readonly sub?: string; readonly stat?: string; readonly img?: string; readonly credit?: string; readonly color?: string }[];
};
export type ColumnsScene = Base & {
  readonly type: "columns";
  readonly cols: readonly { readonly label: string; readonly value: number; readonly color?: string; readonly highlight?: boolean }[];
  readonly legend?: readonly { readonly label: string; readonly color: string }[];
  readonly note?: string;
};

export type Scene = TimelineScene | ColumnsScene | PitchScene | IntroScene | ScanScene | TechniqueScene | LabelScene | HeatScene | BarsScene | RepeatScene | JudgeScene | RevealScene;

export type Episode = {
  readonly slug: string;
  readonly title: string;
  readonly accent?: string;
  readonly scenes: readonly Scene[];
};
