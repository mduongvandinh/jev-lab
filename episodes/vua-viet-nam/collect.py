"""Các vua Việt Nam từ nhà Ngô (939) tới nhà Nguyễn (1945), theo bảng của bài "Vua Việt Nam" trên Wikipedia tiếng Việt (CC BY-SA).

Bỏ thời truyền thuyết (Hồng Bàng) và các chúa Trịnh, chúa Nguyễn. Với mỗi vua: tên, triều đại, thế thứ, năm trị vì (chữ trong bảng),
liên kết bài riêng; rồi lấy đoạn mở đầu + ảnh đại diện của bài riêng (20 bài/request).
Ra: data/kings.jsonl
"""
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json  # noqa: E402
from htmltables import tables  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIRST, SKIP = "Nhà Ngô", ("Chúa Trịnh", "Chúa Nguyễn", "Quê hương", "Đọc thêm", "Thái thượng hoàng", "Những chính thể", "Vua các quốc gia")


def col(header, *names):
    for n in names:
        for i, h in enumerate(header):
            if h[0].startswith(n):
                return i
    return None


if __name__ == "__main__":
    h = get_json("https://vi.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "parse", "page": "Vua Việt Nam", "prop": "text", "format": "json"}))["parse"]["text"]["*"]
    parts = re.split(r"<h[23][^>]*>(.*?)</h[23]>", h)
    kings, started = [], False
    for k in range(1, len(parts), 2):
        title = re.sub("<[^>]+>", "", parts[k]).strip()
        started = started or title.startswith(FIRST)
        if not started or any(s in title for s in SKIP):
            continue
        dyn = "Nhà Mạc" if title.startswith("Bắc triều") else "Lê trung hưng" if title.startswith("Nam triều") else "Lê sơ" if "Lê sơ" in title else re.sub(r"\s*\(.*", "", title).strip()
        for t in tables(parts[k + 1]):
            if not t or len(t) < 2:
                continue
            head = t[0]
            ci, cr, cs = col(head, "Vua", "Hoàng đế"), col(head, "Trị vì"), col(head, "Thế thứ")
            if ci is None or cr is None:
                continue
            for row in t[1:]:
                if len(row) <= max(ci, cr) or not row[ci][0]:
                    continue
                link = next((l for l in row[ci][1] if not l.startswith(("Tập_tin:", "File:"))), None)
                last = max(i for i, h in enumerate(head) if h[0].startswith("Trị vì"))  # nhóm "Trị vì": bắt đầu, dấu nối, kết thúc
                end = row[last][0] if last != cr and last < len(row) else ""
                kings.append({"name": row[ci][0], "link": urllib.parse.unquote(link) if link else None, "dynasty": dyn, "section": title,
                              "reign_text": f"{row[cr][0]} – {end}" if end else row[cr][0], "lineage": row[cs][0] if cs is not None and cs < len(row) else ""})
    print("KINGS", len(kings))
    links = [k["link"] for k in kings if k["link"]]
    info = {}
    for i in range(0, len(links), 20):
        batch = [l.replace("_", " ") for l in links[i:i + 20]]
        q = get_json("https://vi.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "titles": "|".join(batch), "prop": "extracts|pageimages", "exintro": 1, "explaintext": 1, "exlimit": 20,
            "piprop": "thumbnail", "pithumbsize": 400, "redirects": 1, "format": "json"}))["query"]
        alias = {r["from"]: r["to"] for r in q.get("redirects", []) + q.get("normalized", [])}
        pages = {p["title"]: p for p in q["pages"].values()}
        for t in batch:
            p = pages.get(alias.get(t, t), {})
            info[t] = {"extract": (p.get("extract") or "")[:2500], "thumb": (p.get("thumbnail") or {}).get("source")}
        time.sleep(1)
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    with open(os.path.join(HERE, "data", "kings.jsonl"), "w", encoding="utf-8") as f:
        for n, k in enumerate(kings):
            f.write(json.dumps({"id": f"k{n}", **k, **info.get((k["link"] or "").replace("_", " "), {"extract": "", "thumb": None})}, ensure_ascii=False) + "\n")
    print("DONE", len(kings), "with extract", sum(1 for k in kings if info.get((k["link"] or "").replace("_", " "), {}).get("extract")))
