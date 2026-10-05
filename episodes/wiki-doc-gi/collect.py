"""Người Việt đọc gì trên Wikipedia: top 1.000 bài mỗi tháng (10/2025–9/2026) của vi.wikipedia, API Pageviews của Wikimedia.

Gộp theo bài, bỏ trang đặc biệt/Trang Chính; lấy đoạn mở đầu (API MediaWiki, 20 bài/request) cho TOP_N bài nhiều lượt xem nhất.
Ra: data/monthly.json {tháng: [[bài, lượt xem]...]}, data/articles.jsonl {id, title, views, months, peak_month, extract}
"""
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MONTHS = [(2025, m) for m in (10, 11, 12)] + [(2026, m) for m in range(1, 10)]
TOP_N = 1500
SKIP_PREFIX = ("Đặc_biệt:", "Trang_Chính", "Wikipedia:", "Tập_tin:", "Thể_loại:", "Bản_mẫu:", "Thảo_luận", "Chủ_đề:")

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    monthly, total, seen_months, peak = {}, {}, {}, {}
    for y, m in MONTHS:
        key = f"{y}-{m:02d}"
        arts = get_json(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/vi.wikipedia/all-access/{y}/{m:02d}/all-days")["items"][0]["articles"]
        rows = [(a["article"], a["views"]) for a in arts if not a["article"].startswith(SKIP_PREFIX) and a["article"] != "-"]
        monthly[key] = rows
        for t, v in rows:
            total[t] = total.get(t, 0) + v
            seen_months[t] = seen_months.get(t, 0) + 1
            if v > peak.get(t, ("", 0))[1]:
                peak[t] = (key, v)
        print("MONTH", key, len(rows), flush=True)
        time.sleep(1)
    json.dump(monthly, open(os.path.join(HERE, "data", "monthly.json"), "w", encoding="utf-8"), ensure_ascii=False)
    top = sorted(total, key=lambda t: -total[t])[:TOP_N]
    # Gom 20 bài mỗi request (API MediaWiki: đoạn mở đầu + mô tả ngắn + ảnh đại diện) để không bị giới hạn tốc độ
    info = {}
    for i in range(0, len(top), 20):
        batch = [t.replace("_", " ") for t in top[i:i + 20]]
        q = get_json("https://vi.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "titles": "|".join(batch), "prop": "extracts|description|pageimages", "exintro": 1, "explaintext": 1,
            "exlimit": 20, "piprop": "thumbnail", "pithumbsize": 400, "redirects": 1, "format": "json"}))["query"]
        alias = {r["from"]: r["to"] for r in q.get("redirects", []) + q.get("normalized", [])}
        pages = {p["title"]: p for p in q["pages"].values()}
        for t in batch:
            p = pages.get(alias.get(t, t), {})
            info[t] = {"description": p.get("description"), "extract": (p.get("extract") or "")[:1200], "thumb": (p.get("thumbnail") or {}).get("source")}
        print("SUMMARY", i, flush=True)
        time.sleep(1)
    with open(os.path.join(HERE, "data", "articles.jsonl"), "w", encoding="utf-8") as f:
        for i, t in enumerate(top):
            f.write(json.dumps({"id": f"w{i}", "title": t.replace("_", " "), "views": total[t], "months": seen_months[t], "peak_month": peak[t][0],
                                "peak_views": peak[t][1], **info[t.replace("_", " ")]}, ensure_ascii=False) + "\n")
    print("DONE articles", len(top), "unique", len(total))
