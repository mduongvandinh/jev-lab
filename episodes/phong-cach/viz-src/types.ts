export type Mode = "internal" | "public";

export type Tile = {
  readonly id: string;
  readonly palette: readonly string[];
  readonly labels: Readonly<Record<string, readonly [string, number]>>; // trục -> [nhãn, xác suất]
  readonly author?: string | null;
};

export type Candidate = {
  readonly combo: Readonly<Record<string, string>>;
  readonly coherent: number; // xác suất "có" (Noul)
  readonly novelty: number; // điểm 0–4 (Score)
  readonly closest: string;
  readonly closestProb: number;
  readonly appeal: number; // 0–4
  readonly pass: boolean;
};

export type Winner = {
  readonly name: string;
  readonly tagline: string;
  readonly palette: readonly string[];
  readonly rules: readonly string[];
  readonly combo: Readonly<Record<string, string>>;
};

export type VizData = {
  readonly source: string;
  readonly scanned: number;
  readonly kept: number;
  readonly excluded: readonly { readonly id: string; readonly reason: string }[];
  readonly tiles: readonly Tile[];
  readonly axisCounts: Readonly<Record<string, Readonly<Record<string, number>>>>;
  readonly heat: { readonly rows: readonly string[]; readonly cols: readonly string[]; readonly counts: readonly (readonly number[])[] };
  readonly candidates: readonly Candidate[];
  readonly winner: Winner;
};
