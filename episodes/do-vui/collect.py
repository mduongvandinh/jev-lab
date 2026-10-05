"""Toàn văn bài Wikipedia tiếng Việt của 99 vua (danh sách từ ../vua-viet-nam/data/kings.jsonl), tách thành đoạn.

API MediaWiki chỉ trả toàn văn 1 bài mỗi request: giãn cách 1 giây.
Ra: data/paragraphs.jsonl {id, king_id, king, text}
"""
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    kings = read_jsonl(os.path.join(HERE, "..", "vua-viet-nam", "data", "kings.jsonl"))
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    n = 0
    with open(os.path.join(HERE, "data", "paragraphs.jsonl"), "w", encoding="utf-8") as f:
        for k in kings:
            if not k["link"]:
                continue
            q = get_json("https://vi.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "titles": k["link"].replace("_", " "), "prop": "extracts",
                                                                                      "explaintext": 1, "redirects": 1, "format": "json"}))["query"]
            text = next(iter(q["pages"].values())).get("extract") or ""
            for para in text.split("\n"):
                para = para.strip()
                if len(para.split()) >= 12 and not para.startswith("=="):
                    f.write(json.dumps({"id": f"p{n}", "king_id": k["id"], "king": k["name"], "text": para[:1500]}, ensure_ascii=False) + "\n")
                    n += 1
            time.sleep(1)
    print("PARAGRAPHS", n)
