"""Biến dữ liệu thật + đáp án Jev thành episode.json (9 cảnh) và narration.json cho tập "thời tiết".

"Ngày đẹp" = Jev chấm độ dễ chịu khi ra ngoài >= 2,5/4 (giữa "Ổn" và "Dễ chịu").
Classification using confidence: kiểu ngày có confidence < 0,6 thì lùi về nhãn rộng "có mưa" / "không mưa".
"""
import json
import os
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GOOD, CONF = 2.5, 0.6
KIND_VI = {"hot_sunny": "Nắng nóng", "warm_pleasant": "Ấm, dễ chịu", "cool_pleasant": "Mát, khô ráo", "cold": "Rét",
           "muggy": "Oi ẩm, nồm", "drizzle_gray": "Âm u, mưa phùn", "rainy": "Mưa", "heavy_rain_storm": "Mưa lớn, bão"}
KIND_ICON = {"hot_sunny": "🥵", "warm_pleasant": "🌤️", "cool_pleasant": "🍃", "cold": "🥶", "muggy": "🌫️", "drizzle_gray": "🌦️", "rainy": "🌧️", "heavy_rain_storm": "⛈️"}
WET = {"drizzle_gray", "rainy", "heavy_rain_storm"}
COMFORT_VI = ["Rất tệ", "Khó chịu", "Ổn", "Dễ chịu", "Lý tưởng"]


def code_icon(c):
    return "☀️" if c in (0, 1) else "⛅" if c in (2, 3) else "🌫️" if c in (45, 48) else "🌦️" if c in (51, 53, 55, 56, 57) else "⛈️" if c >= 95 else "🌧️"


def vn(n, d=0):
    s = f"{n:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def day_card(d, tone=None):
    dd = d["date"][8:] + "/" + d["date"][5:7]
    rain = f"mưa {vn(d['precipitation_sum'], 1)} mm" if d["precipitation_sum"] >= 0.1 else "không mưa"
    return {"icon": code_icon(d["weather_code"]), "title": f"{d['city']} · {dd}", "tone": tone,
            "lines": [f"{vn(d['temperature_2m_min'])}–{vn(d['temperature_2m_max'])}°C", rain, f"ẩm {d['relative_humidity_2m_mean']}%"]}


def main():
    days = {d["id"]: d for d in read_jsonl(os.path.join(HERE, "data", "days.jsonl"))}
    ans = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "answers.jsonl")) if "answers" in r}
    cities = list(dict.fromkeys(d["city"] for d in days.values()))
    rows = []
    for i, r in ans.items():
        a, d = r["answers"], days[i]
        kind, kc = a["kind"]["choice"], a["kind"]["confidence"]
        rows.append({**d, "comfort": a["comfort"]["score"], "kind": kind, "kind_conf": kc, "kind_probs": a["kind"]["probabilities"],
                     "laundry": a["laundry"]["noul"], "umbrella": a["umbrella"]["noul"], "good": a["comfort"]["score"] >= GOOD})
    by_city = defaultdict(list)
    for r in rows:
        by_city[r["city"]].append(r)
    good = {c: sum(r["good"] for r in by_city[c]) for c in cities}
    rank = sorted(cities, key=lambda c: -good[c])
    month_good = {c: [sum(r["good"] for r in by_city[c] if int(r["date"][5:7]) == m) for m in range(1, 13)] for c in cities}
    best_month = {c: max(range(12), key=lambda m: month_good[c][m]) for c in cities}
    unsure = [r for r in rows if r["kind_conf"] < CONF]
    kinds = Counter(r["kind"] for r in rows)
    spend = cost(list(ans.values()))
    cons = json.load(open(os.path.join(HERE, "jev", "consistency.json"))) if os.path.exists(os.path.join(HERE, "jev", "consistency.json")) else []

    random.seed(7)
    sample = random.sample(rows, 160)
    demo = days["Hà Nội|2025-03-12"]
    demo_a = ans[demo["id"]]["answers"]
    examples_ids = ["Hà Nội|2025-01-01", "Đà Lạt|2025-02-10", "TP.HCM|2025-04-20", "Huế|2025-10-28"]
    ex_rows = {r["id"]: r for r in rows}

    def answers_of(r):
        return [
            {"q": "Dễ chịu", "text": f"{vn(r['comfort'], 1)}/4 · {COMFORT_VI[round(r['comfort'])]}", "tone": "good" if r["good"] else "bad"},
            {"q": "Kiểu ngày", "text": KIND_VI[r["kind"]], "prob": r["kind_probs"][r["kind"]]},
            {"q": "Phơi đồ", "text": "Khô được" if r["laundry"] >= 0.5 else "Không khô", "prob": r["laundry"], "tone": "good" if r["laundry"] >= 0.5 else "muted"},
            {"q": "Áo mưa", "text": "Nên mang" if r["umbrella"] >= 0.5 else "Không cần", "prob": r["umbrella"], "tone": "warn" if r["umbrella"] >= 0.5 else "muted"},
        ]

    sure_pick = sorted([r for r in rows if r["kind_conf"] >= 0.9], key=lambda r: r["id"])[::400][:2]
    # Nhãn rộng suy từ nhãn hẹp: xác suất "có mưa" = tổng xác suất các kiểu ngày có mưa (không cần gọi thêm)
    wet_p = lambda r: sum(v for k, v in r["kind_probs"].items() if k in WET)  # noqa: E731
    u_sorted = sorted(unsure, key=lambda r: r["id"])
    u_wet = [r for r in u_sorted if wet_p(r) >= 0.7][::97][:2]
    u_dry = [r for r in u_sorted if wet_p(r) <= 0.3][::53][:1]
    judge_items = []
    for r in [sure_pick[0], u_wet[0], sure_pick[1], u_dry[0], u_wet[1]]:
        top2 = sorted(r["kind_probs"].items(), key=lambda kv: -kv[1])[:2]
        sure = r["kind_conf"] >= CONF
        wp = wet_p(r)
        broad = "Có mưa" if wp >= 0.5 else "Không mưa"
        judge_items.append({"card": day_card(r), "pass": sure,
                            "stamp": f"CHẮC: {KIND_VI[r['kind']].upper()}" if sure else f"CHƯA CHẮC → {broad.upper()}",
                            "metrics": [{"label": KIND_VI[k], "value": v, "text": f"{round(v * 100)}%", "tone": "jev" if j == 0 else "muted"} for j, (k, v) in enumerate(top2)]
                            + [{"label": "Confidence", "value": r["kind_conf"], "text": vn(r["kind_conf"], 2), "tone": "good" if sure else "bad"},
                               {"label": "Cộng dồn: có mưa", "value": wp, "text": f"{round(wp * 100)}%", "tone": "warn"}]})

    win = rank[0]
    hot = {c: sum(r["kind"] == "hot_sunny" for r in by_city[c]) for c in cities}
    hot_city = max(cities, key=hot.get)
    ep = {"slug": "thoi-tiet", "title": "Thành phố nào nhiều ngày đẹp trời nhất?", "accent": "#38bdf8", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · THỜI TIẾT", "headline": "Thành phố nào nhiều ngày đẹp trời nhất?",
         "sub": f"{vn(len(rows))} ngày thời tiết năm 2025 của {len(cities)} thành phố, AI chấm từng ngày"},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · DỮ LIỆU THẬT", "title": "Mỗi thẻ là một ngày", "cards": [day_card(r) for r in sample],
         "total": len(rows), "totalLabel": "đã đọc", "unit": "ngày", "cols": 4, "cardH": 200, "credit": "Dữ liệu: Open-Meteo.com (CC BY 4.0), tái phân tích ERA5"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · MỘT LẦN GỌI, BỐN CÂU", "title": "Hỏi gộp cho rẻ", "cookbook": "Parallel questions",
         "idea": "Mỗi ngày chỉ gửi Jev một request, kèm cả bốn câu hỏi.",
         "stateLines": [f"Hà Nội · 12/03/2025", f"{vn(demo['temperature_2m_min'])}–{vn(demo['temperature_2m_max'])}°C · ẩm {demo['relative_humidity_2m_mean']}%",
                        f"mưa {vn(demo['precipitation_sum'], 1)} mm trong {vn(demo['precipitation_hours'])} giờ · nắng {vn((demo['sunshine_duration'] or 0) / 3600, 1)} giờ"],
         "questions": [{"name": "comfort", "kind": "Score", "text": "Ra ngoài có dễ chịu không?"}, {"name": "kind", "kind": "Choice", "text": "Kiểu ngày nào?"},
                       {"name": "laundry", "kind": "Noul", "text": "Phơi đồ có khô không?"}, {"name": "umbrella", "kind": "Noul", "text": "Có nên mang áo mưa?"}],
         "results": [{"name": "comfort", "value": f"{vn(demo_a['comfort']['score'], 2)} / 4", "tone": "bad"},
                     {"name": "kind", "value": KIND_VI[demo_a["kind"]["choice"]]},
                     {"name": "laundry", "value": f"có: {round(demo_a['laundry']['noul'] * 100)}%", "tone": "muted"},
                     {"name": "umbrella", "value": f"có: {round(demo_a['umbrella']['noul'] * 100)}%", "tone": "warn"}],
         "footer": f"{vn(len(rows))} request, mỗi ngày một lần · tổng {vn(spend['input_tokens'] / 1e6, 2)} triệu token"},
        {"type": "label", "key": "label", "step": "BƯỚC 3 · JEV CHẤM TỪNG NGÀY", "title": "Đáp án kèm mức chắc chắn",
         "examples": [{"card": day_card(ex_rows[i]), "answers": answers_of(ex_rows[i])} for i in examples_ids],
         "tally": {"title": "Kiểu ngày phổ biến nhất", "bars": [{"label": KIND_VI[k], "value": n} for k, n in kinds.most_common(5)]}},
        {"type": "heat", "key": "heat", "step": "BƯỚC 4 · BẢN ĐỒ CẢ NĂM", "title": "Số ngày đẹp mỗi tháng", "rows": cities, "cols": [f"T{m}" for m in range(1, 13)],
         "values": [month_good[c] for c in cities], "highlight": [[i, best_month[c]] for i, c in enumerate(cities)],
         "legend": "Ô sáng viền vàng: tháng đẹp nhất của từng thành phố"},
        {"type": "bars", "key": "bars", "step": "BƯỚC 5 · XẾP HẠNG", "title": "Cả năm có bao nhiêu ngày đẹp?",
         "bars": [{"label": c, "value": good[c], "text": f"{good[c]} ngày", "tone": "good" if i == 0 else "jev", "sub": f"đẹp nhất: tháng {best_month[c] + 1}"} for i, c in enumerate(rank)],
         "note": "Ngày đẹp: Jev chấm từ 2,5/4 trở lên"},
        {"type": "judge", "key": "judge", "step": "BƯỚC 6 · KHI JEV PHÂN VÂN", "title": "Chưa chắc thì nói rộng ra", "cookbook": "Classification using confidence", "items": judge_items},
    ]}
    if cons:
        ep["scenes"].append({"type": "repeat", "key": "repeat", "step": "BƯỚC 7 · HỎI LẠI 15 LẦN", "title": "Đáp án có đổi không?", "cookbook": "Self-consistency",
                             "rows": [{"label": c["id"].replace("|", " · "), "values": c["comfort"], "min": 0, "max": 4,
                                       "text": f"lệch {vn(c['comfort_sd'], 3)}",
                                       "zoom": [round(min(c["comfort"]) - 0.1, 1), round(max(c["comfort"]) + 0.1, 1)]} for c in cons],
                             "verdict": f"Mỗi chấm là một lần hỏi lại điểm dễ chịu (thang 0–4, thanh dưới phóng to). {sum(c['kind_same'] == c['runs'] for c in cons)}/{len(cons)} ngày giữ nguyên kiểu ngày cả 15 lần."})
    ep["scenes"].append({"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": f"{win}: {good[win]} ngày đẹp",
                         "tagline": f"Nhiều nhất trong {len(cities)} thành phố. Hà Nội đẹp nhất vào tháng {best_month['Hà Nội'] + 1}, TP.HCM vào tháng {best_month['TP.HCM'] + 1}.",
                         "stats": [{"value": vn(len(rows)), "label": "ngày đã chấm"}, {"value": vn(len(unsure)), "label": "ngày Jev chưa chắc kiểu"},
                                   {"value": f"{vn(spend['usd'], 2)} USD", "label": "tiền gọi Jev"}],
                         "bullets": [f"Ít ngày đẹp nhất: {rank[-1]} ({good[rank[-1]]} ngày)",
                                     f"Phơi đồ khô được nhiều nhất: {max(cities, key=lambda c: sum(r['laundry'] >= 0.5 for r in by_city[c]))}",
                                     f"Nhiều ngày nắng nóng nhất: {hot_city} ({hot[hot_city]} ngày)"],
                         "gridTitle": "Tháng đẹp nhất để đi", "grid": [{"label": c, "value": f"tháng {best_month[c] + 1}"} for c in rank],
                         "footnote": "Số liệu tái phân tích của Open-Meteo, không phải trạm đo, và thường ghi nhận mưa nhỏ nhiều hơn thực tế. \"Đẹp\" là đánh giá của Jev từ con số, mỗi người cảm nhận khác."})
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"good": good, "rank": rank, "best_month": {c: m + 1 for c, m in best_month.items()}, "unsure": len(unsure), "rows": len(rows),
             "kinds": dict(kinds), "cost": spend, "laundry": {c: sum(r["laundry"] >= 0.5 for r in by_city[c]) for c in cities},
             "umbrella": {c: sum(r["umbrella"] >= 0.5 for r in by_city[c]) for c in cities},
             "consistency": [{k: v for k, v in c.items() if k not in ("comfort", "umbrella", "kinds")} for c in cons],
             "demo": {"comfort": demo_a["comfort"]["score"], "kind": demo_a["kind"]["choice"], "laundry": demo_a["laundry"]["noul"], "umbrella": demo_a["umbrella"]["noul"]},
             "judge": [j["stamp"] for j in judge_items], "hot": hot}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False))


if __name__ == "__main__":
    main()
