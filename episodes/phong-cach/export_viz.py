"""Gom dữ liệu thật của lượt chạy thành viz/src/data/viz.json cho video mô phỏng.

Ứng viên qua vòng: mạch lạc (Noul) >= 0.6, mới lạ (Score) >= 2.5, và Jev chọn "none_fits"
hoặc xác suất giống trường phái gần nhất < 0.5. Xếp hạng: mạch lạc × mới lạ × độ "không giống ai" × hấp dẫn.
Phong cách thắng cuộc (tên, quy tắc, bảng màu) đọc từ out/style.json (viết sau khi xem kết quả).
"""
import glob
import json
import os
import random
import re

from axes import AXES

ROOT = os.path.dirname(os.path.abspath(__file__))


def reason_group(text):
    t = (text or "").lower()
    if re.search(r"blood|gore|horror|macabre|violen", t):
        return "bạo lực / máu"
    if re.search(r"text|meme|poster|parody|logo|caption|title|comic", t):
        return "chủ yếu là chữ / meme"
    if re.search(r"real|selfie|public figure|identifiable|person", t):
        return "ảnh người thật"
    return "nội dung nhạy cảm"


def score_candidate(c):
    j = c["jev"]
    coherent = j["coherent"]["noul"]
    novelty = j["novelty"]["score"]
    closest = j["closest"]["choice"]
    closest_prob = j["closest"]["probabilities"][closest]
    appeal = j["appeal"]["score"]
    unlike = 1.0 if closest == "none_fits" else 1 - closest_prob
    passed = coherent >= 0.6 and novelty >= 2.5 and (closest == "none_fits" or closest_prob < 0.5)
    return {"combo": c["combo"], "coherent": coherent, "novelty": novelty, "closest": closest, "closestProb": closest_prob,
            "appeal": appeal, "pass": passed, "rank": coherent * (novelty / 4) * unlike * (0.5 + appeal / 8)}


def ranked_candidates():
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "jev", "candidates_scored.jsonl"), encoding="utf-8")]
    return sorted((score_candidate(c) for c in rows if "jev" in c), key=lambda c: -c["rank"])


def main():
    kept = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "data", "kept.jsonl"), encoding="utf-8")}
    excluded = []
    for f in sorted(glob.glob(os.path.join(ROOT, "descriptions", "*.json"))):
        excluded += [{"id": d["id"], "reason": reason_group(d.get("exclude_reason"))} for d in json.load(open(f, encoding="utf-8")) if d.get("exclude")]
    labels = {}
    for l in open(os.path.join(ROOT, "jev", "labels.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if "answers" in r:
            labels[r["id"]] = {a: [v["choice"], round((v.get("probabilities") or {}).get(v["choice"], 0), 2)] for a, v in r["answers"].items()}
    tiles = [{"id": i, "palette": [p["hex"] for p in kept[i]["palette"]], "labels": labels[i], "author": kept[i].get("author")} for i in labels if i in kept]
    random.seed(3)
    random.shuffle(tiles)
    stats = json.load(open(os.path.join(ROOT, "out", "map.json"), encoding="utf-8"))
    rows = [k for k in AXES["medium"]["labels"] if k != "unclear"]
    cols = [k for k in AXES["technique"]["labels"] if k != "unclear"]
    pair = stats["pairs"]["medium|technique"]
    counts = [[pair.get(f"{r}|{c}", 0) for c in cols] for r in rows]
    cands = ranked_candidates()
    # Video: xen ứng viên bị loại và qua vòng, kết thúc bằng ứng viên thắng
    passed = [c for c in cands if c["pass"]]
    failed = [c for c in cands if not c["pass"]]
    show = [x for pair_ in zip(failed[:6], passed[1:7]) for x in pair_][:9] + passed[:1]
    style = json.load(open(os.path.join(ROOT, "out", "style.json"), encoding="utf-8"))
    viz = {
        "source": "Civitai", "scanned": len(kept), "kept": len(labels), "excluded": excluded, "tiles": tiles[:400],
        "axisCounts": stats["singles"], "heat": {"rows": rows, "cols": cols, "counts": counts},
        "candidates": [{k: v for k, v in c.items() if k != "rank"} for c in show], "winner": style["winner"],
    }
    os.makedirs(os.path.join(ROOT, "viz", "src", "data"), exist_ok=True)
    json.dump(viz, open(os.path.join(ROOT, "viz", "src", "data", "viz.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("VIZ tiles", len(viz["tiles"]), "excluded", len(excluded), "candidates", len(show), "passed", len(passed), "/", len(cands))


if __name__ == "__main__":
    main()
