"""Sự nghiệp Cristiano Ronaldo từ Wikipedia tiếng Anh (CC BY-SA): bảng thống kê CLB theo mùa, đội tuyển theo năm,
danh hiệu, mốc đời sống. Kèm ảnh từ Wikimedia Commons có ghi tác giả + giấy phép.

Ra: data/club.json (mùa × giải: ra sân, bàn), data/intl.json, data/honours.json, data/raw_*.html, data/photos.json
"""
import html as H
import json
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://en.wikipedia.org/w/api.php?"


class Tables(HTMLParser):
    """Đọc mọi <table>: trả list bảng, mỗi bảng list hàng, mỗi ô (text, colspan, rowspan)."""

    def __init__(self):
        super().__init__()
        self.tables, self.stack, self.cell, self.skip = [], [], None, 0

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "table":
            self.stack.append([])
        elif tag == "tr" and self.stack:
            self.stack[-1].append([])
        elif tag in ("td", "th") and self.stack:
            self.cell = [[], int(a.get("colspan", 1) or 1), int(a.get("rowspan", 1) or 1)]
        elif tag in ("sup", "style") or ("display:none" in (a.get("style") or "")):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "table" and self.stack:
            self.tables.append(self.stack.pop())
        elif tag in ("td", "th") and self.cell and self.stack and self.stack[-1]:
            self.stack[-1][-1].append((" ".join("".join(self.cell[0]).split()), self.cell[1], self.cell[2]))
            self.cell = None
        elif tag in ("sup", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, d):
        if self.cell is not None and not self.skip:
            self.cell[0].append(d)


def grid(table):
    """Trải rowspan/colspan thành lưới chữ nhật."""
    out, pending = [], {}
    for row in table:
        line, col, it = [], 0, iter(row)
        cells = list(row)
        i = 0
        while i < len(cells) or col in pending:
            if col in pending:
                text, left = pending[col]
                line.append(text)
                pending[col] = (text, left - 1) if left > 1 else None
                if pending[col] is None:
                    del pending[col]
                col += 1
                continue
            text, cs, rs = cells[i]
            i += 1
            for _ in range(cs):
                line.append(text)
                if rs > 1:
                    pending[col] = (text, rs - 1)
                col += 1
        out.append(line)
    return out


def section(n):
    return get_json(API + urllib.parse.urlencode({"action": "parse", "page": "Cristiano_Ronaldo", "prop": "text", "section": n, "format": "json"}))["parse"]["text"]["*"]


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    rev = get_json(API + urllib.parse.urlencode({"action": "query", "titles": "Cristiano_Ronaldo", "prop": "revisions", "rvprop": "timestamp|ids", "format": "json"}))
    meta = next(iter(rev["query"]["pages"].values()))["revisions"][0]
    out = {"revision": meta}
    for name, n in (("club", 37), ("intl", 38), ("honours", 39)):
        h = section(n)
        open(os.path.join(HERE, "data", f"raw_{name}.html"), "w", encoding="utf-8").write(h)
        p = Tables()
        p.feed(h)
        out[name] = [grid(t) for t in p.tables]
        if name == "honours":
            text = re.sub(r"<[^>]+>", "\n", h)
            out["honours_text"] = [l.strip() for l in H.unescape(text).split("\n") if l.strip()]
    json.dump(out, open(os.path.join(HERE, "data", "wiki.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("REV", meta, {k: [len(t) for t in v] for k, v in out.items() if k in ("club", "intl", "honours")})
