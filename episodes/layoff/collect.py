"""Layoff 2026 từ hai nguồn công khai:
1) Tiêu đề tin tức Google News RSS theo từng tháng 1–10/2026 (chỉ tiêu đề + tên báo, không lấy bài).
2) Bình luận Hacker News của người kể chuyện bị cho nghỉ việc (từ 1/1/2025), 25–250 chữ.
Ra: data/news.jsonl, data/stories.jsonl
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json, get_text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
NEWS_Q = ["layoffs", "lays off employees", "job cuts company"]
STORY_Q = ["got laid off", "was laid off", "after being laid off", "since I was laid off", "after my layoff", "laid off last year"]


def clean(t):
    t = re.sub(r"<p>", "\n", t or "")
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    news, seen = [], set()
    for m in range(1, 11):
        a, b = f"2026-{m:02d}-01", (f"2026-{m + 1:02d}-01" if m < 12 else "2027-01-01")
        for q in NEWS_Q:
            url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": f"{q} after:{a} before:{b}", "hl": "en-US", "gl": "US", "ceid": "US:en"})
            root = ET.fromstring(get_text(url))
            for it in root.iter("item"):
                title = it.findtext("title") or ""
                src = it.findtext("source") or ""
                key = re.sub(r"\W+", " ", title.lower())[:90]
                if key in seen:
                    continue
                seen.add(key)
                news.append({"id": f"n{len(news)}", "month": f"2026-{m:02d}", "title": title.rsplit(" - ", 1)[0], "source": src, "date": it.findtext("pubDate")})
            time.sleep(2)
        print("NEWS", a[:7], len(news), flush=True)
    stories, sid = [], set()
    for q in STORY_Q:
        for page in range(5):
            hits = get_json("https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode({"query": f'"{q}"', "tags": "comment", "hitsPerPage": 100, "page": page, "numericFilters": "created_at_i>1735689600"}))["hits"]
            if not hits:
                break
            for h in hits:
                t = clean(h.get("comment_text"))
                if h["objectID"] in sid or not 25 <= len(t.split()) <= 250:
                    continue
                sid.add(h["objectID"])
                stories.append({"id": f"hn{h['objectID']}", "created": h["created_at"][:10], "text": t})
            time.sleep(0.5)
        print("STORIES", q, len(stories), flush=True)
    for name, rows in (("news", news), ("stories", stories)):
        with open(os.path.join(HERE, "data", f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("DONE news", len(news), "stories", len(stories))
