"""Tin tuyển dụng (Who is hiring) và hồ sơ tìm việc (Who wants to be hired) trên Hacker News, 10/2025–10/2026.

Mỗi bài tháng lấy cả cây bình luận qua API Algolia (1 request/bài); chỉ giữ bình luận cấp 1 (mỗi cái là một tin/hồ sơ).
Ra: data/posts.jsonl {id, kind: hiring|seeking, month, text}
"""
import html
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def clean(t):
    t = re.sub(r"<p>", "\n", t or "")
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t).strip()


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    stories = get_json("https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&hitsPerPage=60")["hits"]
    rows = []
    for s in stories:
        kind = "hiring" if "Who is hiring" in s["title"] else "seeking" if "Who wants to be hired" in s["title"] else None
        if not kind or s["created_at"] < "2025-10-01":
            continue
        tree = get_json(f"https://hn.algolia.com/api/v1/items/{s['objectID']}")
        n = 0
        for c in tree.get("children", []):
            text = clean(c.get("text"))
            if len(text.split()) < 12:
                continue
            rows.append({"id": f"hn{c['id']}", "kind": kind, "month": s["created_at"][:7], "text": text})
            n += 1
        print(kind, s["created_at"][:7], n, flush=True)
        time.sleep(1)
    with open(os.path.join(HERE, "data", "posts.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("POSTS", len(rows))
