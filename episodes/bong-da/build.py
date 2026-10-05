"""Biến cú sút World Cup 2022 + đáp án Jev thành episode.json cho tập "bóng đá".

So sánh (không tính penalty): Jev (chỉ đọc mô tả) vs xG của StatsBomb vs kết quả thật.
- AUC: khả năng xếp cú nguy hiểm hơn lên trên. - Brier: sai số xác suất (thấp hơn = tốt hơn).
- Hiệu chỉnh: chia 10 nhóm theo xác suất Jev trên nửa số trận (train), áp tỷ lệ bàn thật của nhóm cho nửa còn lại (test).
"""
import json
import os
import random
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KIND_VI = {"penalty": "Penalty", "direct_free_kick": "Đá phạt trực tiếp", "one_on_one": "Đối mặt thủ môn", "close_range": "Cận thành", "header": "Đánh đầu",
           "box_shot": "Sút trong vòng cấm", "long_range": "Sút xa", "tight_angle": "Góc hẹp"}
BODY_VI = {"Left Foot": "chân trái", "Right Foot": "chân phải", "Head": "đánh đầu", "Other": "bộ phận khác"}


def vn(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def auc(ps, ys):
    pos = [p for p, y in zip(ps, ys) if y]
    neg = [p for p, y in zip(ps, ys) if not y]
    return sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg))


def brier(ps, ys):
    return sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ys)


def short(name):
    return {"Lionel Andrés Messi Cuccittini": "Messi", "Kylian Mbappé Lottin": "Mbappé", "Ángel Fabián Di María Hernández": "Di María"}.get(name, name.split()[-1])


def main():
    shots = {s["id"]: s for s in read_jsonl(os.path.join(HERE, "data", "shots.jsonl"))}
    res = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "answers.jsonl")) if "answers" in r}
    photos = json.load(open(os.path.join(HERE, "data", "photos.json"), encoding="utf-8"))
    cons = json.load(open(os.path.join(HERE, "jev", "consistency.json"), encoding="utf-8"))
    rows = [{**shots[i], "p": r["answers"]["goal"]["noul"], "q": r["answers"]["quality"]["score"], "kind": r["answers"]["kind"]["choice"],
             "kind_p": r["answers"]["kind"]["probabilities"][r["answers"]["kind"]["choice"]]} for i, r in res.items()]
    op = [r for r in rows if r["shot_type"] != "Penalty"]
    ys = [int(r["goal"]) for r in op]
    jp, xg = [r["p"] for r in op], [r["xg"] for r in op]
    a_jev, a_xg = auc(jp, ys), auc(xg, ys)
    matches = sorted({r["match"] for r in op})
    train = set(matches[::2])
    tr = [r for r in op if r["match"] in train]
    te = [r for r in op if r["match"] not in train]
    ps = sorted(r["p"] for r in tr)
    edges = [ps[int(len(ps) * k / 10)] for k in range(1, 10)]
    binof = lambda p: sum(p >= e for e in edges)  # noqa: E731
    rate = {}
    for k in range(10):
        g = [int(r["goal"]) for r in tr if binof(r["p"]) == k]
        rate[k] = (sum(g) + 0.5) / (len(g) + 5)
    yte = [int(r["goal"]) for r in te]
    base = sum(int(r["goal"]) for r in tr) / len(tr)
    b_raw, b_cal = brier([r["p"] for r in te], yte), brier([rate[binof(r["p"])] for r in te], yte)
    b_xg, b_base = brier([r["xg"] for r in te], yte), brier([base] * len(te), yte)
    cal_sum = sum(rate[binof(r["p"])] for r in te)
    buckets = []
    for lo, hi, lab in [(0, 0.2, "dưới 20%"), (0.2, 0.4, "20–40%"), (0.4, 1.01, "từ 40%")]:
        b = [r for r in op if lo <= r["p"] < hi]
        buckets.append({"label": f"Jev nói {lab}", "n": len(b), "rate": sum(r["goal"] for r in b) / len(b), "mean": statistics.mean(r["p"] for r in b)})
    spend = cost(list(res.values()))
    final = sorted([r for r in rows if r["match"] == "Argentina – France" and r["goal"] and r["shot_type"] == "Open Play"], key=lambda r: r["minute"])
    messi_miss = next(r for r in rows if r["player"].startswith("Lionel") and r["shot_type"] == "Open Play" and r["match"] == "Netherlands – Argentina")
    photo = lambda r: photos.get({"Messi": "messi", "Mbappé": "mbappe", "Di María": "dimaria"}.get(short(r["player"]), ""), None)  # noqa: E731

    def card(r, img=False):
        ph = photo(r) if img else None
        c = {"icon": None if ph else "⚽", "title": f"{short(r['player'])} · {r['minute']}'", "sub": r["match"],
             "lines": [f"{vn(r['distance_m'], 1)} m · {BODY_VI.get(r['body_part'], r['body_part'])}", f"{r['defenders_in_way']} người chắn"]}
        if ph:
            c.update({"img": f"bong-da/{ {'Messi': 'messi', 'Mbappé': 'mbappe', 'Di María': 'dimaria'}[short(r['player'])] }.jpg", "credit": ph["credit"], "lines": None})
        return c

    random.seed(9)
    sample = random.sample(rows, 150)
    ex = [messi_miss] + final[:3]
    ep = {"slug": "bong-da", "title": "AI có đoán được cú sút nào thành bàn?", "accent": "#22c55e", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · BÓNG ĐÁ", "headline": "AI có đoán được cú sút nào thành bàn?",
         "sub": f"{vn(len(rows))} cú sút ở World Cup 2022. AI chỉ được đọc tình huống, không biết ai sút"},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · DỮ LIỆU THẬT", "title": "Mỗi thẻ là một cú sút", "cards": [card(r) for r in sample],
         "total": len(rows), "totalLabel": "đã đọc", "unit": "cú sút", "cols": 3, "cardH": 200,
         "credit": "Dữ liệu mở của StatsBomb: vị trí bóng, cầu thủ và thủ môn lúc sút, 64 trận"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · CHỈ ĐỌC TÌNH HUỐNG", "title": "Jev không biết ai sút", "cookbook": "Parallel questions",
         "idea": "Tên cầu thủ, chỉ số xG và kết quả đều bị giấu. Jev chỉ thấy tình huống.",
         "stateLines": [f"cách khung thành {vn(messi_miss['distance_m'], 1)} m · góc nhìn {vn(messi_miss['angle_deg'], 0)}°", f"{messi_miss['defenders_in_way']} hậu vệ chắn · chân trái · không bị áp sát",
                        "tình huống: tấn công thường · có đường chuyền"],
         "questions": [{"name": "goal", "kind": "Noul", "text": "Cú này có thành bàn không?"}, {"name": "quality", "kind": "Score", "text": "Cơ hội ngon đến mức nào?"},
                       {"name": "kind", "kind": "Choice", "text": "Kiểu cơ hội gì?"}],
         "results": [{"name": "goal", "value": f"{round(messi_miss['p'] * 100)}%", "tone": "warn"}, {"name": "quality", "value": f"{vn(messi_miss['q'], 2)}/4"},
                     {"name": "kind", "value": KIND_VI[messi_miss["kind"]], "tone": "good"}],
         "footer": f"Đó là cú sút của Messi phút {messi_miss['minute']} trận gặp Hà Lan. xG chuyên môn: {round(messi_miss['xg'] * 100)}%. Kết quả: ra ngoài."},
        {"type": "pitch", "key": "pitch", "step": "BƯỚC 3 · CẢ GIẢI TRÊN MỘT SÂN", "title": "Mỗi chấm là một cú sút",
         "points": [{"x": round(r["x"], 1), "y": round(r["y"], 1), "p": round(r["p"], 2), "g": r["goal"]} for r in sorted(rows, key=lambda r: r["id"])],
         "legend": "Chấm càng to, Jev càng tin sẽ thành bàn. Viền trắng: bàn thắng thật."},
        {"type": "label", "key": "label", "step": "BƯỚC 4 · ĐỐI CHIẾU", "title": "Jev, xG và kết quả thật",
         "examples": [{"card": card(r, img=True), "answers": [{"q": "Jev", "text": f"{round(r['p'] * 100)}%", "tone": "jev"}, {"q": "xG chuyên môn", "text": f"{round(r['xg'] * 100)}%", "tone": "muted"},
                                                              {"q": "Kết quả", "text": "VÀO" if r["goal"] else "trượt", "tone": "good" if r["goal"] else "bad"}]} for r in ex],
         "tally": {"title": "Kiểu cơ hội Jev nhận ra", "bars": [{"label": KIND_VI[k], "value": n} for k, n in Counter(r["kind"] for r in rows).most_common(5)]}},
        {"type": "bars", "key": "rank", "step": "BƯỚC 5 · JEV XẾP HẠNG ĐÚNG KHÔNG?", "title": "Jev càng tin, càng hay vào",
         "bars": [{"label": b["label"], "value": b["rate"], "text": f"{round(b['rate'] * 100)}% vào", "sub": f"{vn(b['n'])} cú · Jev đoán TB {round(b['mean'] * 100)}%",
                   "tone": "good" if i == 2 else "jev"} for i, b in enumerate(buckets)],
         "note": f"Xếp đúng cú nào nguy hiểm hơn: Jev {round(a_jev * 100)}%, mô hình xG chuyên dụng {round(a_xg * 100)}%. Nhưng con số của Jev quá lạc quan: đoán {round(sum(jp))} bàn, thật chỉ {sum(ys)}."},
        {"type": "repeat", "key": "repeat", "step": "BƯỚC 6 · HỎI LẠI 15 LẦN", "title": "Jev có đổi ý không?", "cookbook": "Self-consistency",
         "rows": [{"label": f"{short(c['player'])} · xG {round(c['xg'] * 100)}%", "values": c["values"], "min": 0, "max": 1, "text": f"lệch {vn(c['sd'], 3)}",
                   "zoom": [round(min(c["values"]) - 0.05, 2), round(max(c["values"]) + 0.05, 2)]} for c in cons],
         "verdict": "Đổi ý rất ít: lạc quan thì lạc quan một cách nhất quán, nên sửa được bằng hiệu chỉnh."},
        {"type": "bars", "key": "calib", "step": "BƯỚC 7 · HIỆU CHỈNH BẰNG DỮ LIỆU", "title": "Sai số dự đoán", "cookbook": "Đặt ngưỡng từ dữ liệu có nhãn",
         "bars": [{"label": "Jev thô", "value": b_raw, "text": vn(b_raw, 3), "tone": "bad"}, {"label": "Đoán bừa", "value": b_base, "text": vn(b_base, 3), "tone": "muted", "sub": "tỷ lệ chung cho mọi cú"},
                  {"label": "Jev hiệu chỉnh", "value": b_cal, "text": vn(b_cal, 3), "tone": "good", "sub": "học trên nửa số trận"}, {"label": "xG chuyên dụng", "value": b_xg, "text": vn(b_xg, 3), "tone": "jev"}],
         "note": f"Thử trên {len(set(r['match'] for r in te))} trận chưa dùng để hiệu chỉnh. Càng ngắn càng tốt. Sau hiệu chỉnh, Jev đoán {round(cal_sum)} bàn, thật {sum(yte)}."},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": "Biết cú nào nguy hiểm, nhưng quá lạc quan",
         "tagline": "Chỉ đọc mô tả, Jev xếp hạng cơ hội gần bằng mô hình chuyên dụng. Hiệu chỉnh một lần bằng dữ liệu thật là dùng được con số.",
         "stats": [{"value": vn(len(rows)), "label": "cú sút đã chấm"}, {"value": f"{round(a_jev * 100)}% / {round(a_xg * 100)}%", "label": "xếp hạng đúng: Jev / xG"},
                   {"value": f"{vn(spend['usd'] * 100, 1)} cent", "label": "tiền gọi Jev"}],
         "bullets": [], "gridTitle": "Bàn thắng trong trận chung kết", "gridCols": 1,
         "grid": [{"label": f"{short(r['player'])} {r['minute']}'", "value": f"Jev {round(r['p'] * 100)}% · xG {round(r['xg'] * 100)}%"} for r in final],
         "footnote": "Dữ liệu StatsBomb, không tính penalty và loạt luân lưu khi so sánh. xG của StatsBomb được huấn luyện trên hàng trăm nghìn cú sút; Jev không được huấn luyện cho việc này."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"rows": len(rows), "open_play_n": len(op), "goals_np": sum(ys), "jev_sum": round(sum(jp)), "auc_jev": round(a_jev, 3), "auc_xg": round(a_xg, 3),
             "brier": {"raw": round(b_raw, 4), "cal": round(b_cal, 4), "xg": round(b_xg, 4), "base": round(b_base, 4)}, "test_matches": len(set(r["match"] for r in te)),
             "test_goals": sum(yte), "cal_sum": round(cal_sum), "buckets": buckets, "cost": spend, "kinds": Counter(r["kind"] for r in rows).most_common(),
             "messi_miss": {k: messi_miss[k] for k in ("minute", "distance_m", "angle_deg", "p", "q", "kind", "xg")},
             "final": [(short(r["player"]), r["minute"], round(r["p"], 2), round(r["xg"], 2)) for r in final], "consistency": [(c["player"], c["sd"], c["xg"]) for c in cons]}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(facts, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
