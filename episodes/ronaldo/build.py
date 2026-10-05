"""Hồ sơ số liệu Cristiano Ronaldo từ bảng thống kê Wikipedia (data/wiki.json) -> episode.json + facts.json.

Không dùng Jev: đây là tổng hợp số liệu có sẵn, mọi con số cộng từ bảng theo mùa / theo năm.
"""
import json
import os
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CLUB_COLOR = {"Sporting CP": "#16a34a", "Manchester United": "#dc2626", "Real Madrid": "#e5e7eb", "Juventus": "#9ca3af", "Al-Nassr": "#facc15"}
CLUB_VI = {"Sporting CP": "Sporting", "Manchester United": "Man United", "Real Madrid": "Real Madrid", "Juventus": "Juventus", "Al-Nassr": "Al-Nassr"}
COMP = ["VĐQG", "Cúp QG", "Cúp LĐ", "Châu lục", "Khác"]


def num(x):
    x = (x or "").replace(",", "").strip()
    return int(x) if x.isdigit() else 0


def vn(n):
    return f"{n:,}".replace(",", ".")


def main():
    w = json.load(open(os.path.join(HERE, "data", "wiki.json"), encoding="utf-8"))
    photos = json.load(open(os.path.join(HERE, "data", "photos.json"), encoding="utf-8"))
    rows = [r for r in w["club"][0][2:] if r[1] not in ("Total",) and r[0] != "Career total"]
    career = next(r for r in w["club"][0] if r[0] == "Career total")
    seasons = []
    for r in rows:
        club = "Sporting CP" if r[0].startswith("Sporting") else r[0]
        seasons.append({"club": club, "team": r[0], "season": r[1], "apps": num(r[13]), "goals": num(r[14]),
                        "comp": [num(r[4]), num(r[6]), num(r[8]), num(r[10]), num(r[12])]})
    stints = []
    for s in seasons:
        if stints and stints[-1]["club"] == s["club"]:
            st = stints[-1]
        else:
            st = {"club": s["club"], "from": s["season"], "apps": 0, "goals": 0}
            stints.append(st)
        st["to"], st["apps"], st["goals"] = s["season"], st["apps"] + s["apps"], st["goals"] + s["goals"]
    by_season = OrderedDict()
    for s in seasons:
        e = by_season.setdefault(s["season"], {"goals": 0, "club": s["club"]})
        e["goals"] += s["goals"]
        if s["goals"] >= 1:
            e["club"] = s["club"]
    peak = max(by_season, key=lambda k: by_season[k]["goals"])
    comp = defaultdict(lambda: [0] * 5)
    for s in seasons:
        comp[s["club"]] = [a + b for a, b in zip(comp[s["club"]], s["comp"])]
    clubs = list(CLUB_COLOR)
    intl = [r for r in w["intl"][0][2:] if r[0] == "Portugal" and r[1].isdigit()]
    por = next(r for r in w["intl"][0] if r[0] == "Portugal" and r[1] == "Total")
    por_apps, por_goals = num(por[6]), num(por[7])
    club_apps, club_goals = num(career[13]), num(career[14])
    trophies = {"Sporting": 1, "Man United": 9, "Real Madrid": 15, "Juventus": 5, "Al-Nassr": 2, "Bồ Đào Nha": 3}
    img = lambda k: f"ronaldo/{k}.jpg"  # noqa: E731
    stint_img = {0: "madeira", 1: "mu1", 2: "ballon", 3: "juve", 4: "mu2", 5: "nassr"}
    stint_sub = {0: "Ra mắt chuyên nghiệp năm 17 tuổi", 1: "£12 triệu, kỷ lục nước Anh cho cầu thủ tuổi teen",
                 2: "£80 triệu, kỷ lục chuyển nhượng thế giới khi đó", 3: "€100 triệu, cao nhất cho cầu thủ trên 30 tuổi",
                 4: "Trở lại Old Trafford", 5: "Đội trưởng, ra mắt 22/1/2023"}
    first_team = [s for s in stints if not (s["club"] == "Sporting CP" and s["goals"] == 0 and s["apps"] <= 2)]
    sp = [s for s in stints if s["club"] == "Sporting CP"]
    merged = [{"club": "Sporting CP", "from": sp[0]["from"], "to": sp[-1]["to"], "apps": sum(s["apps"] for s in sp), "goals": sum(s["goals"] for s in sp)}] + [s for s in stints if s["club"] != "Sporting CP"]

    def yr(a, b):
        return f"{a[:4]}–{b[:2]}{b[5:]}" if a != b else a

    ep = {"slug": "ronaldo", "title": "Cristiano Ronaldo qua những con số", "accent": "#e11d48", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "HỒ SƠ SỐ LIỆU · CR7", "headline": f"Cristiano Ronaldo: {vn(club_goals + por_goals)} bàn thắng",
         "sub": "Từ cậu bé nghèo ở Madeira tới Al-Nassr. Mọi con số theo Wikipedia, 4/10/2026"},
        {"type": "timeline", "key": "childhood", "step": "PHẦN 1 · TUỔI THƠ", "title": "Cậu bé đảo Madeira", "items": [
            {"years": "5/2/1985", "title": "Sinh ra ở Funchal, Madeira", "sub": "Con út trong 4 anh chị em, nhà nghèo, ở chung một phòng", "img": img("madeira"), "credit": photos["madeira"]["credit"]},
            {"years": "1992–1995", "title": "CLB Andorinha", "sub": "Nơi bố làm người trông đồ thi đấu bán thời gian"},
            {"years": "1995–1997", "title": "CLB Nacional", "sub": "Hai năm ở đội trẻ"},
            {"years": "1997 · 12 tuổi", "title": "Sporting CP, giá £1.500", "sub": "Rời đảo Madeira sang Lisbon, vào lò đào tạo trẻ"},
            {"years": "Tuổi thiếu niên", "title": "Mổ tim vì nhịp tim nhanh", "sub": "Vài ngày sau ca mổ đã tập lại"}]},
        {"type": "timeline", "key": "clubs", "step": "PHẦN 2 · 6 CHẶNG CÂU LẠC BỘ", "title": "Ra sân và bàn thắng", "items": [
            {"years": yr(s["from"], s["to"]), "title": CLUB_VI[s["club"]], "sub": stint_sub[i], "stat": f"{s['goals']} bàn\n{s['apps']} trận", "color": CLUB_COLOR[s["club"]],
             "img": img(stint_img[i]) if i else None, "credit": photos[stint_img[i]]["credit"] if i else None} for i, s in enumerate(merged)]},
        {"type": "columns", "key": "seasons", "step": "PHẦN 3 · TỪNG MÙA GIẢI", "title": "Bàn thắng mỗi mùa cho CLB",
         "cols": [{"label": k[2:4], "value": v["goals"], "color": CLUB_COLOR[v["club"]], "highlight": k == peak} for k, v in by_season.items()],
         "legend": [{"label": CLUB_VI[c], "color": CLUB_COLOR[c]} for c in clubs], "note": f"Nhãn là năm bắt đầu mùa (14 = 2014–15). Đỉnh cao: mùa {peak} với {by_season[peak]['goals']} bàn. Mùa 2026–27 đang diễn ra."},
        {"type": "heat", "key": "comps", "step": "PHẦN 4 · GHI BÀN Ở ĐÂU", "title": "Bàn thắng theo giải đấu", "rows": [CLUB_VI[c] for c in clubs], "cols": COMP,
         "values": [comp[c] for c in clubs], "highlight": [[clubs.index("Real Madrid"), 0], [clubs.index("Real Madrid"), 3]],
         "legend": "Châu lục: Champions League và các cúp châu lục. Khác: siêu cúp, cúp thế giới các CLB."},
        {"type": "columns", "key": "portugal", "step": "PHẦN 5 · ĐỘI TUYỂN BỒ ĐÀO NHA", "title": f"{por_goals} bàn sau {por_apps} trận",
         "cols": [{"label": r[1][2:], "value": num(r[7]), "color": "#16a34a", "highlight": num(r[7]) == max(num(x[7]) for x in intl)} for r in intl],
         "note": "Bàn thắng mỗi năm (03 = 2003), tính cả trận giao hữu."},
        {"type": "bars", "key": "trophies", "step": "PHẦN 6 · DANH HIỆU TẬP THỂ", "title": f"{sum(trophies.values())} danh hiệu",
         "bars": [{"label": k, "value": v, "text": f"{v}", "tone": "good" if v == max(trophies.values()) else "jev"} for k, v in trophies.items()],
         "note": "Gồm 5 Champions League (1 với Man United, 4 với Real Madrid), Euro 2016 và 2 UEFA Nations League."},
        {"type": "reveal", "key": "reveal", "kicker": "TỔNG KẾT SỰ NGHIỆP", "headline": f"{vn(club_apps + por_apps)} trận · {vn(club_goals + por_goals)} bàn",
         "tagline": "Cầu thủ ghi nhiều bàn chính thức nhất lịch sử bóng đá, và ra sân nhiều nhất trong các cầu thủ không phải thủ môn.",
         "stats": [{"value": "5", "label": "Quả bóng vàng"}, {"value": "5", "label": "Champions League"}, {"value": "4", "label": "Chiếc giày vàng châu Âu"}],
         "bullets": ["Cầu thủ duy nhất ghi 100 bàn cho 4 CLB khác nhau", "Vua phá lưới ở 4 giải VĐQG khác nhau", "7 lần vua phá lưới Champions League"],
         "gridTitle": "Bàn mỗi trận ở từng CLB", "gridCols": 2,
         "grid": [{"label": CLUB_VI[c], "value": f"{sum(s['goals'] for s in merged if s['club'] == c) / sum(s['apps'] for s in merged if s['club'] == c):.2f}".replace(".", ",")} for c in clubs],
         "footnote": "Nguồn: Wikipedia tiếng Anh, bài \"Cristiano Ronaldo\" (bản ngày 4/10/2026, CC BY-SA). Ảnh: Wikimedia Commons, ghi tác giả trên từng ảnh. Số liệu mùa 2026–27 còn thay đổi."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"club": [club_apps, club_goals], "portugal": [por_apps, por_goals], "total": [club_apps + por_apps, club_goals + por_goals],
             "stints": merged, "peak": [peak, by_season[peak]["goals"]], "by_season": {k: v["goals"] for k, v in by_season.items()},
             "comp": {c: comp[c] for c in clubs}, "intl_by_year": {r[1]: num(r[7]) for r in intl}, "trophies": trophies, "revision": w["revision"]}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False))


if __name__ == "__main__":
    main()
