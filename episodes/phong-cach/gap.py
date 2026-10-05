"""Tìm tổ hợp phong cách chưa xuất hiện trong mẫu, rồi nhờ Jev thật chấm độ mạch lạc / mới lạ / tính ứng dụng.

Bước 1 (candidates): tổ hợp medium × technique × palette × era có 0 tác phẩm, nhưng mọi cặp thành phần
đều đã xuất hiện ≥ MIN_PAIR lần (thành phần hợp nhau, chỉ chưa ai ghép trọn bộ). Xếp theo độ hợp lý.
Bước 2 (evaluate): mỗi ứng viên một request Jev (Noul + Score + Choice + Score).
Ra: out/map.json (tần suất để vẽ), out/candidates.json, jev/candidates_scored.jsonl
"""
import itertools
import json
import math
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from axes import AXES
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from jevcall import decide  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
STYLE_AXES = ["medium", "technique", "palette", "era"]
MIN_PAIR, TOP_N, MIN_PROB = 2, 120, 0.5

KNOWN_STYLES = {
    "art_nouveau_deco": "Art Nouveau / Art Deco poster style", "ukiyo_e": "Ukiyo-e woodblock print",
    "vaporwave_synthwave": "Vaporwave / synthwave", "cyberpunk": "Cyberpunk neon sci-fi", "steampunk": "Steampunk",
    "pop_art": "Pop art / comic halftone", "bauhaus_modernist": "Bauhaus / modernist geometric", "impressionism": "Impressionism",
    "pixel_art": "Pixel art / retro game", "low_poly": "Low poly 3D", "risograph_zine": "Risograph / zine print",
    "anime_cel": "Anime / cel-shaded illustration", "gothic_illuminated": "Gothic / illuminated manuscript / stained glass",
    "folk_naive": "Folk / naive art", "botanical_watercolor": "Botanical watercolor illustration",
    "dark_fantasy": "Dark fantasy painting", "none_fits": "None of these named styles describes it well",
}


def load_labels():
    """Nhãn Jev của từng ảnh; loạt ảnh gần trùng của cùng tác giả (cùng tổ hợp phong cách) chỉ tính một lần."""
    authors = {json.loads(l)["id"]: json.loads(l).get("author") for l in open(os.path.join(ROOT, "data", "kept.jsonl"), encoding="utf-8")}
    rows, seen = [], set()
    for l in open(os.path.join(ROOT, "jev", "labels.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if "answers" not in r:
            continue
        # Nhãn yếu (xác suất chọn < MIN_PROB) coi như chưa rõ, không tính vào bản đồ
        row = {a: (v["choice"] if (v.get("probabilities") or {}).get(v["choice"], 0) >= MIN_PROB else "unclear")
               for a, v in r["answers"].items()} | {"id": r["id"]}
        key = (authors.get(r["id"]), tuple(row[a] for a in STYLE_AXES))
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    return rows


def build_candidates(rows):
    full = Counter(tuple(r[a] for a in STYLE_AXES) for r in rows)
    pairs = Counter()
    for r in rows:
        for a, b in itertools.combinations(STYLE_AXES, 2):
            pairs[(a, r[a], b, r[b])] += 1
    values = {a: [v for v in AXES[a]["labels"] if v not in ("unclear",)] for a in STYLE_AXES}
    cands = []
    for combo in itertools.product(*(values[a] for a in STYLE_AXES)):
        if full[combo]:
            continue
        pc = [pairs[(a, combo[i], b, combo[j])] for (i, a), (j, b) in itertools.combinations(enumerate(STYLE_AXES), 2)]
        if min(pc) < MIN_PAIR:
            continue
        cands.append({"combo": dict(zip(STYLE_AXES, combo)), "pair_counts": pc,
                      "plausibility": round(math.exp(sum(math.log(c) for c in pc) / len(pc)), 2)})
    cands.sort(key=lambda c: -c["plausibility"])
    # Đa dạng hóa: mỗi cặp (medium, technique) tối đa 4, mỗi trường phái tối đa 25 ứng viên
    picked, per, per_era = [], Counter(), Counter()
    for c in cands:
        k = (c["combo"]["medium"], c["combo"]["technique"])
        if per[k] < 4 and per_era[c["combo"]["era"]] < 25:
            picked.append(c)
            per[k] += 1
            per_era[c["combo"]["era"]] += 1
        if len(picked) >= TOP_N:
            break
    singles = {a: Counter(r[a] for r in rows) for a in AXES}
    heat = {f"{a}|{b}": {f"{x}|{y}": n for (aa, x, bb, y), n in pairs.items() if aa == a and bb == b}
            for a, b in itertools.combinations(STYLE_AXES, 2)}
    return picked, {"n": len(rows), "singles": {a: dict(c) for a, c in singles.items()}, "pairs": heat, "full_combos_seen": len(full)}


def evaluate(c):
    combo = c["combo"]
    state = {
        "candidate_style": {a: {"label": v, "meaning": AXES[a]["labels"][v]} for a, v in combo.items()},
        "evidence": {"corpus": "1000 safe-for-work AI images from Civitai, labeled by Jev",
                     "observed_count_of_this_exact_combination": 0,
                     "pair_counts_of_its_ingredients": c["pair_counts"]},
    }
    questions = {
        "coherent": {"type": "noul", "instructions": "Could one artwork combine ALL of these traits at once and still look visually coherent and intentional?",
                     "criteria": {"true": "The traits can coexist in one deliberate, coherent look", "false": "The traits contradict each other or would look accidental"}},
        "novelty": {"type": "score", "instructions": "How distinct is this combination from widely known, named art styles?",
                    "criteria": ["It is simply a well-known named style", "A common variation of a known style", "An uncommon twist on a known style",
                                 "Rarely seen; only loosely related to known styles", "Clearly distinct from any widely known named style"]},
        "closest": {"type": "choice", "instructions": "Which widely known named style is this combination closest to?", "criteria": KNOWN_STYLES},
        "appeal": {"type": "score", "instructions": "How well would this style work for eye-catching short-form social media visuals?",
                   "criteria": ["Poorly: hard to read or unappealing at phone size", "Weak", "Acceptable", "Good", "Excellent: striking and readable at phone size"]},
    }
    try:
        res = decide({"model": "typesafe/jev-1.13", "state": state, "questions": questions})
        return {**c, "jev": res["response"]["answers"]}
    except Exception as e:
        return {**c, "error": str(e)[:200]}


def main():
    rows = load_labels()
    cands, stats = build_candidates(rows)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    json.dump(stats, open(os.path.join(ROOT, "out", "map.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(cands, open(os.path.join(ROOT, "out", "candidates.json"), "w"), ensure_ascii=False, indent=1)
    print("ROWS", len(rows), "COMBOS_SEEN", stats["full_combos_seen"], "CANDIDATES", len(cands), flush=True)
    if "--no-jev" in sys.argv:
        return
    with ThreadPoolExecutor(max_workers=6) as pool, open(os.path.join(ROOT, "jev", "candidates_scored.jsonl"), "w", encoding="utf-8") as f:
        for r in pool.map(evaluate, cands):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("EVAL_DONE", flush=True)


if __name__ == "__main__":
    main()
