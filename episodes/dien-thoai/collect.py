"""Bình luận công khai trên Hacker News (API Algolia, không cần key) nhắc tới iPhone, Samsung Galaxy, Google Pixel, từ 1/1/2025.

Giữ bình luận 25–220 chữ; mỗi truy vấn tối đa PER_QUERY bình luận; bỏ trùng. HTML được làm sạch thành chữ.
Ra: data/comments.jsonl
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SINCE = 1735689600  # 2025-01-01
QUERIES = {"iphone": ["iphone"], "samsung": ["samsung galaxy", "samsung phone"], "pixel": ["pixel phone", "google pixel", "grapheneos pixel"],
           "switch": ["switched to iphone", "switched to android", "back to android", "back to iphone"]}
PER_QUERY = 400


def clean(t):
    t = re.sub(r"<p>", "\n", t or "")
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t).strip()


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    seen, rows = set(), []
    for group, qs in QUERIES.items():
        for q in qs:
            got = 0
            for page in range(20):
                url = "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode(
                    {"query": q, "tags": "comment", "hitsPerPage": 100, "page": page, "numericFilters": f"created_at_i>{SINCE}"})
                hits = get_json(url)["hits"]
                if not hits:
                    break
                for h in hits:
                    text = clean(h.get("comment_text"))
                    n = len(text.split())
                    if h["objectID"] in seen or not 25 <= n <= 220:
                        continue
                    seen.add(h["objectID"])
                    rows.append({"id": h["objectID"], "query": q, "group": group, "author": h.get("author"), "created": h["created_at"][:10],
                                 "story": h.get("story_title"), "text": text})
                    got += 1
                if got >= PER_QUERY:
                    break
                time.sleep(0.5)
            print("Q", q, got, flush=True)
    with open(os.path.join(HERE, "data", "comments.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("COMMENTS", len(rows))
