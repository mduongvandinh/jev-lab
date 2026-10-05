"""Biến tiêu đề + lượt xem + đáp án Jev thành episode.json cho tập "tiêu đề video".

Lượt xem so với chính kênh: ratio = view / trung vị view của kênh (video 10–400 ngày tuổi, kênh có >= 4 video).
"Nổ view" = ratio >= 1,5. So tỷ lệ nổ view giữa tiêu đề có / không có đặc điểm, kiểm định hoán vị 5.000 lần.
"""
import json
import math
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HIT = 1.5
FEAT_VI = {"curiosity": "Gây tò mò", "emotion": "Cảm xúc mạnh", "concrete": "Hứa hẹn cụ thể", "stakes": "Quy mô cực lớn", "personal": "\"Tôi đã làm…\"",
           "negative": "Cảnh báo, sai lầm", "explain": "Giải thích vì sao", "product": "Nói về sản phẩm", "number": "Có con số", "question": "Câu hỏi", "short": "Ngắn ≤ 6 chữ"}
FORMAT_VI = {"challenge_stunt": "Thử thách", "product_review": "Đánh giá sản phẩm", "science_explainer": "Giải thích khoa học", "engineering_build": "Chế tạo",
             "news_business": "Tin tức, kinh tế", "history_story": "Lịch sử, câu chuyện", "other": "Khác"}


def vn(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def feats(a, t):
    f = {k: a[k]["score"] >= 2.5 for k in ("curiosity", "emotion", "concrete")}
    f.update({k: a[k]["noul"] >= 0.5 for k in ("stakes", "personal", "negative", "explain", "product")})
    f.update({"number": bool(re.search(r"\d", t)), "question": "?" in t, "short": len(t.split()) <= 6})
    return f


def perm_p(on, off, n=5000):
    hit = lambda xs: sum(x >= HIT for x in xs) / len(xs)  # noqa: E731
    d, pool, c = hit(on) - hit(off), on + off, 0
    rnd = random.Random(1)
    for _ in range(n):
        rnd.shuffle(pool)
        c += abs(hit(pool[: len(on)]) - hit(pool[len(on):])) >= abs(d) - 1e-12
    return c / n


def main():
    allv = {v["id"]: v for v in read_jsonl(os.path.join(HERE, "data", "videos.jsonl"))}
    res = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "answers.jsonl")) if "answers" in r}
    rows = [v for v in allv.values() if 10 <= v["age_days"] <= 400 and v["id"] in res]
    bych = defaultdict(list)
    for v in rows:
        bych[v["channel"]].append(v)
    rows = [v for v in rows if len(bych[v["channel"]]) >= 4]
    med = {c: statistics.median(x["views"] for x in xs) for c, xs in bych.items()}
    for v in rows:
        v["ratio"] = v["views"] / med[v["channel"]]
        v["a"] = res[v["id"]]["answers"]
        v["f"] = feats(v["a"], v["title"])
    base = sum(v["ratio"] >= HIT for v in rows) / len(rows)
    stats = []
    for k in FEAT_VI:
        on = [v["ratio"] for v in rows if v["f"][k]]
        off = [v["ratio"] for v in rows if not v["f"][k]]
        if len(on) >= 20 and len(off) >= 20:
            stats.append({"k": k, "n": len(on), "hit_on": sum(x >= HIT for x in on) / len(on), "hit_off": sum(x >= HIT for x in off) / len(off), "p": perm_p(on, off)})
    stats.sort(key=lambda s: -s["hit_on"])
    chans = sorted([c for c in bych if len(bych[c]) >= 9], key=lambda c: -len(bych[c]))[:9]
    prof_keys = ["curiosity", "emotion", "stakes", "personal", "negative", "explain", "product", "number"]
    prof = [[round(100 * sum(v["f"][k] for v in rows if v["channel"] == c) / sum(1 for v in rows if v["channel"] == c)) for k in prof_keys] for c in chans]
    spend = cost(list(res.values()))
    nchan = len({v["channel"] for v in allv.values()})

    def card(v):
        return {"img": f"tieu-de-video/thumbs/{v['id']}.jpg", "title": v["title"], "credit": v["channel"]}

    random.seed(4)
    sample = random.sample(list(allv.values()), 120)
    demo = next(v for v in rows if v["channel"] == "MrBeast")
    da = demo["a"]
    picks = {"hi_hit": max((v for v in rows if v["a"]["curiosity"]["score"] >= 3), key=lambda v: v["ratio"]),
             "hi_flop": min((v for v in rows if v["a"]["curiosity"]["score"] >= 3), key=lambda v: v["ratio"]),
             "lo_hit": max((v for v in rows if v["a"]["curiosity"]["score"] < 2), key=lambda v: v["ratio"]),
             "lo_flop": min((v for v in rows if v["a"]["curiosity"]["score"] < 2), key=lambda v: v["ratio"]),
             "mid": sorted(rows, key=lambda v: abs(v["ratio"] - 1))[3]}
    ex = sorted(rows, key=lambda v: v["id"])[::60][:4]

    def ratio_txt(r):
        return f"x{vn(r)} view kênh"

    ep = {"slug": "tieu-de-video", "title": "Tiêu đề kiểu nào giúp video nổ view?", "accent": "#ef4444", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · TIÊU ĐỀ VIDEO", "headline": "Tiêu đề kiểu nào giúp video nổ view?",
         "sub": f"{len(allv)} video của {nchan} kênh YouTube lớn, AI chấm từng tiêu đề"},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · DỮ LIỆU THẬT", "title": "Tiêu đề và lượt xem thật", "cards": [card(v) for v in sample],
         "total": len(allv), "totalLabel": "đã đọc", "unit": "tiêu đề", "cols": 3, "cardH": 250,
         "credit": "Ảnh và tiêu đề thuộc về các kênh; lượt xem lấy từ RSS công khai của YouTube ngày 5/10/2026"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · BIẾN CHỮ THÀNH SỐ", "title": "Mỗi tiêu đề thành 9 cột số", "cookbook": "Autoresearch feature discovery",
         "idea": "Jev chỉ thấy tiêu đề, không thấy tên kênh hay lượt xem.",
         "stateLines": [f"\"{demo['title']}\""],
         "questions": [{"name": "curiosity", "kind": "Score", "text": "Gây tò mò đến mức nào?"}, {"name": "emotion", "kind": "Score", "text": "Cảm xúc mạnh cỡ nào?"},
                       {"name": "stakes", "kind": "Noul", "text": "Quy mô, rủi ro cực lớn?"}, {"name": "personal", "kind": "Noul", "text": "\"Tôi đã làm…\"?"},
                       {"name": "negative", "kind": "Noul", "text": "Cảnh báo, sai lầm?"}, {"name": "format", "kind": "Choice", "text": "Kiểu video gì?"}],
         "results": [{"name": "curiosity", "value": f"{vn(da['curiosity']['score'], 2)}/4"}, {"name": "emotion", "value": f"{vn(da['emotion']['score'], 2)}/4"},
                     {"name": "stakes", "value": f"có: {round(da['stakes']['noul'] * 100)}%", "tone": "warn"}, {"name": "personal", "value": f"có: {round(da['personal']['noul'] * 100)}%", "tone": "muted"},
                     {"name": "negative", "value": f"có: {round(da['negative']['noul'] * 100)}%", "tone": "muted"}, {"name": "format", "value": FORMAT_VI[da["format"]["choice"]], "tone": "good"}],
         "footer": "+ 3 câu nữa trong cùng request · số, dấu hỏi, độ dài thì code tự đếm"},
        {"type": "label", "key": "label", "step": "BƯỚC 3 · GHÉP VỚI LƯỢT XEM", "title": "So với chính kênh đó",
         "examples": [{"card": card(v), "answers": [{"q": "Tò mò", "text": f"{vn(v['a']['curiosity']['score'])}/4"},
                                                     {"q": "Kiểu video", "text": FORMAT_VI[v["a"]["format"]["choice"]], "prob": v["a"]["format"]["probabilities"][v["a"]["format"]["choice"]]},
                                                     {"q": "Lượt xem", "text": ratio_txt(v["ratio"]), "tone": "good" if v["ratio"] >= HIT else "muted"}]} for v in ex],
         "tally": {"title": "Kiểu video trong mẫu", "bars": [{"label": FORMAT_VI[k], "value": n} for k, n in Counter(v["a"]["format"]["choice"] for v in rows).most_common(5)]}},
        {"type": "heat", "key": "heat", "step": "BƯỚC 4 · GIỌNG CỦA TỪNG KÊNH", "title": "Mỗi kênh một kiểu tiêu đề", "rows": chans,
         "cols": ["Tò mò", "Cảm xúc", "Cực lớn", "Tôi", "Cảnh báo", "Vì sao", "Sản phẩm", "Số"], "values": prof,
         "highlight": [[i, max(range(len(prof_keys)), key=lambda j: prof[i][j])] for i in range(len(chans))],
         "legend": "% tiêu đề của kênh có đặc điểm đó. Ô viền vàng: nét nổi bật nhất"},
        {"type": "bars", "key": "bars", "step": "BƯỚC 5 · CÓ CÔNG THỨC KHÔNG?", "title": "Tỷ lệ video nổ view",
         "bars": [{"label": FEAT_VI[s["k"]], "value": s["hit_on"], "text": f"{round(s['hit_on'] * 100)}%", "tone": "muted", "sub": f"không có: {round(s['hit_off'] * 100)}%"} for s in stats],
         "note": f"Nổ view: gấp 1,5 lần trung vị của chính kênh. Trung bình chung {round(base * 100)}%. Không chênh lệch nào vượt mức may rủi (kiểm định hoán vị, p > 0,05)."},
        {"type": "judge", "key": "judge", "step": "BƯỚC 6 · ĐỐI CHIẾU", "title": "Tò mò cao có chắc nổ không?",
         "items": [{"card": card(v), "pass": v["ratio"] >= HIT, "stamp": ratio_txt(v["ratio"]).upper(),
                    "metrics": [{"label": "Gây tò mò", "value": v["a"]["curiosity"]["score"] / 4, "text": f"{vn(v['a']['curiosity']['score'])}/4"},
                                {"label": "Cảm xúc", "value": v["a"]["emotion"]["score"] / 4, "text": f"{vn(v['a']['emotion']['score'])}/4", "tone": "warn"},
                                {"label": "Quy mô cực lớn", "value": v["a"]["stakes"]["noul"], "text": f"{round(v['a']['stakes']['noul'] * 100)}%", "tone": "muted"}]}
                   for v in (picks["hi_hit"], picks["hi_flop"], picks["lo_hit"], picks["lo_flop"], picks["mid"])]},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": "Không có công thức tiêu đề thần kỳ",
         "tagline": "Trong cùng một kênh, kiểu tiêu đề không đoán được video nào nổ view. Thứ đo được rõ nhất là mỗi kênh có giọng riêng.",
         "stats": [{"value": str(len(allv)), "label": "tiêu đề đã chấm"}, {"value": "9", "label": "cột số mỗi tiêu đề, 1 lần gọi"},
                   {"value": f"{vn(spend['usd'] * 100, 1)} cent", "label": "tiền gọi Jev"}],
         "bullets": [f"Nói về sản phẩm: {round(next(s for s in stats if s['k'] == 'product')['hit_on'] * 100)}% nổ view, so với {round(next(s for s in stats if s['k'] == 'product')['hit_off'] * 100)}%, chưa đủ chắc",
                     f"Tiêu đề rất ngắn: {round(next(s for s in stats if s['k'] == 'short')['hit_on'] * 100)}% so với {round(next(s for s in stats if s['k'] == 'short')['hit_off'] * 100)}%, cũng chưa đủ chắc",
                     "Muốn biết thật: thử A/B tiêu đề trên chính kênh của bạn"],
         "footnote": f"{len(rows)} video 10–400 ngày tuổi của {len(bych)} kênh, lượt xem tại một thời điểm. Tương quan, không phải nhân quả; ảnh thumbnail và chủ đề cũng ảnh hưởng."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"rows": len(rows), "channels_used": len(bych), "all": len(allv), "nchan": nchan, "base": round(base, 3),
             "stats": [{**s, "hit_on": round(s["hit_on"], 3), "hit_off": round(s["hit_off"], 3)} for s in stats], "chans": dict(zip(chans, prof)), "cost": spend,
             "demo": {"title": demo["title"], **{k: (v.get("score") or v.get("noul") or v.get("choice")) for k, v in da.items()}},
             "picks": {k: (v["channel"], v["title"], round(v["ratio"], 2), v["a"]["curiosity"]["score"]) for k, v in picks.items()},
             "examples": [(v["channel"], v["title"], round(v["ratio"], 2)) for v in ex]}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False, indent=0)[:3500])


if __name__ == "__main__":
    main()
