"""Người Việt đọc gì trên Wikipedia -> episode.json. Tỷ trọng tính theo LƯỢT XEM (không theo số bài).

Bài bị trạm chắn (adult >= 0,7 hoặc crime >= 0,7) chỉ hiện ô khóa với lý do chung, không lộ tên, không lấy ảnh.
Ảnh: chỉ ảnh từ Wikimedia Commons (giấy phép tự do), có tên tác giả + giấy phép trên từng ảnh.
"""
import html
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import UA, cost, get_json, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "..", "..", "viz", "public", "wiki-doc-gi")
TOPIC_VI = {"people": "Con người", "entertainment": "Giải trí", "places": "Địa danh", "history_politics": "Lịch sử, chính trị", "sports": "Thể thao",
            "society_culture": "Văn hóa, xã hội", "science_tech": "Khoa học, công nghệ", "adult": "Người lớn", "crime_disaster": "Vụ án, thảm họa", "other": "Khác"}
SUB_VI = {"politician": "Chính trị gia", "entertainer": "Nghệ sĩ", "athlete": "Vận động viên", "historical": "Nhân vật lịch sử", "business": "Doanh nhân",
          "korean": "Hàn Quốc", "chinese": "Trung Quốc", "vietnamese_show": "Việt Nam", "western": "Âu Mỹ", "anime_games": "Anime, game", "football": "Bóng đá",
          "multi_sport": "Đại hội thể thao", "vietnam_place": "Nơi ở Việt Nam", "country": "Quốc gia", "foreign_place": "Nơi ở nước ngoài", "vn_history": "Lịch sử Việt Nam",
          "world_history": "Lịch sử thế giới", "government": "Nhà nước, thể chế", "holiday": "Lễ hội", "religion_belief": "Tín ngưỡng", "education": "Giáo dục",
          "tech_ai": "Công nghệ, AI", "health": "Sức khỏe", "nature": "Thiên nhiên", "crime": "Vụ án", "disaster": "Thảm họa", "other": "Khác", "adult": "Người lớn"}
WHY_VI = {"news": "Đang có tin tức", "evergreen": "Lúc nào cũng có người đọc", "sports_event": "Đang có giải đấu", "holiday": "Ngày lễ, kỷ niệm",
          "tv_airing": "Phim, chương trình đang chiếu", "scandal_crime": "Vụ việc, bê bối", "death": "Người vừa qua đời", "unclear": "Không rõ"}


def commons_credits(urls):
    """Tác giả + giấy phép của ảnh Commons (50 file/request)."""
    files = {u: urllib.parse.unquote(u.split("/")[-2] if "/thumb/" in u else u.split("/")[-1]) for u in urls}
    out = {}
    names = list(set(files.values()))
    for i in range(0, len(names), 50):
        q = get_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "titles": "|".join("File:" + n for n in names[i:i + 50]),
                                                                                         "prop": "imageinfo", "iiprop": "extmetadata", "format": "json"}))["query"]
        norm = {n["to"]: n["from"] for n in q.get("normalized", [])}
        for p in q["pages"].values():
            md = (p.get("imageinfo") or [{}])[0].get("extmetadata", {})
            artist = html.unescape(re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", ""))).strip()
            artist = "Không rõ tác giả" if not artist or "unknown" in artist.lower() else artist[:30]
            lic = md.get("LicenseShortName", {}).get("value", "")
            if lic:
                out[norm.get(p["title"], p["title"]).replace("File:", "").replace("_", " ")] = f"{artist} · {lic}"
        time.sleep(1)
    return {u: out.get(files[u].replace("_", " ")) for u in urls}


def fetch(url, dest):
    if not os.path.exists(dest):
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            open(dest, "wb").write(r.read())
        time.sleep(0.5)


def main():
    A = {a["id"]: a for a in read_jsonl(os.path.join(HERE, "data", "articles.jsonl"))}
    p1 = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "pass1.jsonl")) if "answers" in r}
    p2 = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "pass2.jsonl")) if "answers" in r}
    P1 = {i: r["answers"] for i, r in p1.items()}
    # Hai ngưỡng kiểu cookbook Guardrails: >= 0,7 (hoặc Jev xếp chủ đề người lớn) thì CHẶN; vùng XEM XÉT thì không hiện lên video nhưng vẫn tính thống kê
    adult = lambda a: a["adult"]["noul"] >= 0.7 or a["topic"]["choice"] == "adult"  # noqa: E731
    blocked = {i: ("nội dung người lớn" if adult(a) else "vụ án có người thật") for i, a in P1.items() if adult(a) or a["crime"]["noul"] >= 0.7}
    review = {i for i, a in P1.items() if i not in blocked and (a["adult"]["noul"] >= 0.1 or a["crime"]["noul"] >= 0.3)}
    safe = [i for i in P1 if i not in blocked and i not in review]
    tot = sum(A[i]["views"] for i in P1)
    share = lambda f: sum(A[i]["views"] for i in P1 if f(i)) / tot  # noqa: E731
    topic = Counter()
    for i, a in P1.items():
        topic[a["topic"]["choice"]] += A[i]["views"]
    sub = Counter()
    for i, r in p2.items():
        if i not in blocked:
            sub[(P1[i]["topic"]["choice"], r["answers"]["sub"]["choice"])] += A[i]["views"]
    why = Counter()
    for i, a in P1.items():
        why[a["why"]["choice"]] += A[i]["views"]
    vn = share(lambda i: P1[i]["vietnam"]["noul"] >= 0.5)
    hist = sorted([i for i in safe if i in p2 and p2[i]["answers"]["sub"]["choice"] == "historical"], key=lambda i: -A[i]["views"])[:8]
    spend = cost(list(p1.values()) + list(p2.values()))
    os.makedirs(PUB, exist_ok=True)
    commons = [i for i in safe if A[i].get("thumb") and "/wikipedia/commons/" in A[i]["thumb"]]
    random.seed(12)
    wall = random.sample(commons, 90) + random.sample(sorted(blocked), 10)
    random.shuffle(wall)
    ex_titles = ["Tết Trung thu", "Trần Hưng Đạo", "Giải vô địch bóng đá thế giới 2026", "Cortis"]
    ex = [next(i for i in safe if A[i]["title"] == t) for t in ex_titles]
    show_imgs = [A[i]["thumb"] for i in set(wall + ex + hist) if i not in blocked and A[i].get("thumb") and "/wikipedia/commons/" in A[i]["thumb"]]
    credits = commons_credits(show_imgs)

    def card(i, sub_line=True):
        if i in blocked:
            return {"title": "", "locked": blocked[i]}
        if i in review:
            return {"title": "", "locked": "cần người xem xét"}
        a = A[i]
        c = {"title": a["title"], "sub": f"{a['views']:,} lượt xem".replace(",", ".") if sub_line else None}
        if a.get("thumb") and "/wikipedia/commons/" in a["thumb"] and credits.get(a["thumb"]):
            fetch(a["thumb"], os.path.join(PUB, f"{i}.jpg"))
            c.update({"img": f"wiki-doc-gi/{i}.jpg", "credit": credits[a["thumb"]]})
        else:
            c["icon"] = "📖"
        return c

    demo = A[ex[0]]
    da = P1[ex[0]]
    judge_ids = sorted(blocked, key=lambda i: A[i]["id"])[:1] + sorted(review, key=lambda i: A[i]["id"])[:1] + [ex[1], ex[2]]
    ep = {"slug": "wiki-doc-gi", "title": "Người Việt đọc gì trên Wikipedia?", "accent": "#6366f1", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · WIKIPEDIA", "headline": "Người Việt đọc gì trên Wikipedia?",
         "sub": f"1.500 bài được đọc nhiều nhất trong 12 tháng, tổng {tot / 1e6:.0f} triệu lượt xem. AI đọc từng bài".replace(".", ",")},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · DỮ LIỆU THẬT", "title": "Top 1.000 bài mỗi tháng", "cards": [card(i) for i in wall], "total": len(A), "totalLabel": "đã đọc",
         "unit": "bài", "excluded": len(blocked) + len(review), "excludedLabel": "không hiện", "cols": 3, "cardH": 230,
         "credit": "Lượt xem Wikipedia tiếng Việt 10/2025–9/2026 (API Pageviews). Ảnh: Wikimedia Commons, tác giả ghi trên ảnh"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · MỘT LẦN GỌI, NĂM CÂU", "title": "Đọc một bài Wikipedia", "cookbook": "Parallel questions · Guardrails",
         "idea": "Hai câu cuối là trạm chắn: từ 0,7 thì chặn, vùng giữa thì để người xem xét.", "stateLines": [demo["title"], (demo.get("extract") or "")[:120] + "…"],
         "questions": [{"name": "topic", "kind": "Choice", "text": "Bài nói về gì?"}, {"name": "why", "kind": "Choice", "text": "Vì sao được đọc?"},
                       {"name": "vietnam", "kind": "Noul", "text": "Có về Việt Nam?"}, {"name": "adult", "kind": "Noul", "text": "Nội dung người lớn?"},
                       {"name": "crime", "kind": "Noul", "text": "Án mạng có người thật?"}],
         "results": [{"name": "topic", "value": TOPIC_VI[da["topic"]["choice"]]}, {"name": "why", "value": WHY_VI[da["why"]["choice"]], "tone": "warn"},
                     {"name": "vietnam", "value": f"có: {round(da['vietnam']['noul'] * 100)}%", "tone": "good"}, {"name": "adult", "value": f"{round(da['adult']['noul'] * 100)}%", "tone": "muted"},
                     {"name": "crime", "value": f"{round(da['crime']['noul'] * 100)}%", "tone": "muted"}]},
        {"type": "judge", "key": "guard", "step": "BƯỚC 3 · TRẠM CHẮN", "title": "Bài nào không được hiện?", "cookbook": "Guardrails for LLMs",
         "items": [{"card": card(i, False), "pass": i not in blocked and i not in review, "stamp": "CHẶN" if i in blocked else "XEM XÉT" if i in review else "CHO QUA",
                    "metrics": [{"label": "Người lớn", "value": P1[i]["adult"]["noul"], "text": f"{round(P1[i]['adult']['noul'] * 100)}%", "tone": "bad"},
                                {"label": "Án mạng người thật", "value": P1[i]["crime"]["noul"], "text": f"{round(P1[i]['crime']['noul'] * 100)}%", "tone": "warn"}]} for i in judge_ids]},
        {"type": "bars", "key": "topics", "step": "BƯỚC 4 · CHỦ ĐỀ", "title": "Lượt đọc chia theo chủ đề",
         "bars": [{"label": TOPIC_VI[k], "value": v / tot, "text": f"{round(100 * v / tot)}%", "tone": "good" if i == 0 else "muted" if k == "adult" else "jev"} for i, (k, v) in enumerate(topic.most_common(8))],
         "note": f"Tính theo lượt xem. {round(vn * 100)}% lượt đọc là chủ đề Việt Nam."},
        {"type": "label", "key": "tree", "step": "BƯỚC 5 · XẾP VÀO CÂY CHỦ ĐỀ", "title": "Chủ đề lớn, rồi chủ đề con", "cookbook": "Hierarchical classification",
         "examples": [{"card": card(i), "answers": [{"q": "Cấp 1", "text": TOPIC_VI[P1[i]["topic"]["choice"]], "prob": P1[i]["topic"]["probabilities"][P1[i]["topic"]["choice"]]},
                                                    {"q": "Cấp 2", "text": SUB_VI[p2[i]["answers"]["sub"]["choice"]], "prob": p2[i]["answers"]["sub"]["probabilities"][p2[i]["answers"]["sub"]["choice"]]}]} for i in ex],
         "tally": {"title": "Chủ đề con được đọc nhiều nhất (% lượt xem)", "bars": [{"label": f"{SUB_VI[s]}", "value": round(100 * v / tot)} for (t, s), v in sub.most_common(4)]}},
        {"type": "bars", "key": "why", "step": "BƯỚC 6 · VÌ SAO ĐỌC", "title": "Lý do một bài được đọc",
         "bars": [{"label": WHY_VI[k], "value": v / tot, "text": f"{round(100 * v / tot)}%", "tone": "warn" if i == 0 else "jev"} for i, (k, v) in enumerate(why.most_common()) if k != "unclear"][:6],
         "note": f"Jev đoán từ nội dung bài và tháng có lượt xem cao nhất; {round(100 * why['unclear'] / tot)}% lượt xem không rõ lý do."},
        {"type": "timeline", "key": "history", "step": "BƯỚC 7 · NHÂN VẬT LỊCH SỬ", "title": "Được đọc nhiều nhất",
         "items": [{"years": f"{A[i]['views']:,} lượt".replace(",", "."), "title": A[i]["title"], "sub": (A[i].get("description") or "")[:70],
                    **({"img": card(i)["img"], "credit": card(i)["credit"]} if card(i).get("img") else {})} for i in hist[:6]]},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": f"{round(100 * topic['people'] / tot)}% lượt đọc là về con người",
         "tagline": f"Chính trị gia và nhân vật lịch sử dẫn đầu, rồi tới giải trí và bóng đá. {round(vn * 100)}% lượt đọc là chủ đề Việt Nam.",
         "stats": [{"value": "1.500", "label": "bài đã chấm"}, {"value": str(len(blocked)), "label": "bài bị chặn"}, {"value": f"{spend['usd'] * 100:.0f} cent", "label": "tiền gọi Jev"}],
         "bullets": [f"Đọc nhiều nhất: {A['w0']['title']}, {A['w0']['views'] / 1e6:.1f} triệu lượt".replace(".", ","), f"{sum(1 for i in P1 if A[i]['months'] == 12)} bài có mặt trong top 1.000 cả 12 tháng",
                     f"Tin tức chiếm {round(100 * why['news'] / tot)}% lượt đọc, chủ đề lúc nào cũng đọc chiếm {round(100 * why['evergreen'] / tot)}%"],
         "gridTitle": "Đọc nhiều nhất cả năm", "gridCols": 1,
         "grid": [{"label": A[i]["title"][:34], "value": f"{A[i]['views'] / 1e6:.2f} triệu".replace(".", ",")} for i in sorted(safe, key=lambda i: -A[i]["views"])[:5]],
         "footnote": "Lượt xem gồm cả một phần lưu lượng tự động mà Wikimedia chưa lọc hết. Chủ đề và lý do là phán đoán của Jev từ đoạn mở đầu bài viết."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"articles": len(A), "views": tot, "blocked": Counter(blocked.values()), "review": len(review), "topic": {k: round(v / tot, 3) for k, v in topic.most_common()},
             "sub": {f"{t}/{s}": round(v / tot, 3) for (t, s), v in sub.most_common(10)}, "why": {k: round(v / tot, 3) for k, v in why.most_common()}, "vietnam": round(vn, 3),
             "history": [(A[i]["title"], A[i]["views"]) for i in hist], "top": [(A[f"w{k}"]["title"], A[f"w{k}"]["views"]) for k in range(5)],
             "examples": [(A[i]["title"], P1[i]["topic"]["choice"], p2[i]["answers"]["sub"]["choice"]) for i in ex], "cost": spend,
             "demo": {"title": demo["title"], "topic": da["topic"]["choice"], "why": da["why"]["choice"]}}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(facts, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
