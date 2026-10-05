"""Thu thập tác phẩm DeviantArt qua RSS công khai, lọc theo lựa chọn của nghệ sĩ, tải ảnh thu nhỏ, đo bảng màu.

Loại bỏ: nghệ sĩ từ chối AI (isAiUseDisallowed, robots noai/noimageai), tác phẩm do AI tạo, nội dung người lớn.
Lịch sự: giãn cách 1,1 giây mỗi request tới deviantart.com (robots.txt: Crawl-delay 1). Lưu tiến độ để chạy tiếp.
Dùng: python3 collect.py [số tác phẩm cần giữ, mặc định 1000]
"""
import html
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
THUMBS = os.path.join(ROOT, "thumbs")
UA = {"User-Agent": "Mozilla/5.0 (style-gap research; respects noai flags)"}
DELAY = 1.1
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

QUERIES = [
    "watercolor", "oil painting", "ink drawing", "charcoal", "pixel art", "low poly", "vaporwave", "art nouveau",
    "ukiyo-e", "surrealism", "cyberpunk", "steampunk", "gothic art", "minimalism", "abstract painting", "impressionism",
    "cubism", "papercut", "collage art", "isometric", "linocut", "stained glass", "embroidery art", "mosaic",
    "chibi", "concept art", "matte painting", "fractal", "glitch art", "risograph", "cel shading", "sketchbook",
    "botanical illustration", "folk art", "art deco", "pointillism", "solarpunk", "dieselpunk", "claymation", "graffiti",
]


def fetch(url, binary=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def rss_items(query, offset):
    q = urllib.parse.urlencode({"type": "deviation", "q": query, "offset": offset})
    xml = fetch(f"https://backend.deviantart.com/rss.xml?{q}")
    items = []
    for block in xml.split("<item>")[1:]:
        link = re.search(r"<link>(https://www\.deviantart\.com/[^<]+/art/[^<]+)</link>", block)
        thumbs = re.findall(r'<media:thumbnail url="([^"]+)"', block)
        if not link or not thumbs:
            continue
        did = re.search(r"-(\d+)$", link.group(1))
        items.append({
            "id": did.group(1) if did else link.group(1),
            "url": link.group(1),
            "title": html.unescape(re.search(r"<title>(.*?)</title>", block, re.S).group(1).strip()),
            "author": (re.search(r'<media:credit role="author"[^>]*>([^<]+)</media:credit>', block) or [None, ""])[1],
            "rating": (re.search(r"<media:rating>([^<]+)</media:rating>", block) or [None, ""])[1],
            "thumb": html.unescape(thumbs[-1]),  # ảnh 300px
            "query": query,
        })
    return items


def page_flags(url, did):
    """Cờ của chính tác phẩm (không phải tác phẩm liên quan trên cùng trang)."""
    h = fetch(url)
    robots = " ".join(re.findall(r'<meta[^>]+name="robots"[^>]+content="([^"]*)"', h)).lower()
    t = h.replace('\\"', '"')
    m = re.search(r'"deviationId":%s,' % did, t)
    block = t[m.start(): m.start() + 4000] if m else ""
    get = lambda k: (re.search(r'"%s":(true|false)' % k, block) or [None, None])[1]
    return {
        "noaiMeta": "noai" in robots or "noimageai" in robots,
        "isAiUseDisallowed": get("isAiUseDisallowed") == "true",
        "isAiGenerated": get("isAiGenerated") == "true",
        "isMature": get("isMature") == "true",
        "found": bool(m),
    }


def exclusion(item, flags):
    if item["rating"] == "adult" or flags["isMature"]:
        return "nội dung người lớn"
    if flags["noaiMeta"] or flags["isAiUseDisallowed"]:
        return "nghệ sĩ từ chối AI"
    if flags["isAiGenerated"]:
        return "do AI tạo"
    if not flags["found"]:
        return "không đọc được thông tin"
    return None


def palette(path, k=5):
    """5 màu chủ đạo: thu ảnh về 24x24 bằng ffmpeg, gom màu theo lưới 4 mức/kênh."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=24:24", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    buckets = {}
    for i in range(0, len(raw) - 2, 3):
        r, g, b = raw[i], raw[i + 1], raw[i + 2]
        key = (r // 64, g // 64, b // 64)
        acc = buckets.setdefault(key, [0, 0, 0, 0])
        acc[0] += r; acc[1] += g; acc[2] += b; acc[3] += 1
    top = sorted(buckets.values(), key=lambda a: -a[3])[:k]
    total = sum(a[3] for a in top) or 1
    return [{"hex": "#%02x%02x%02x" % (a[0] // a[3], a[1] // a[3], a[2] // a[3]), "share": round(a[3] / total, 3)} for a in top]


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(THUMBS, exist_ok=True)
    cand_path = os.path.join(DATA, "candidates.json")
    if os.path.exists(cand_path):
        candidates = json.load(open(cand_path, encoding="utf-8"))
    else:
        seen, per_query = set(), {}
        for q in QUERIES:
            for off in (0, 60, 120):
                try:
                    for it in rss_items(q, off):
                        if it["id"] not in seen:
                            seen.add(it["id"])
                            per_query.setdefault(q, []).append(it)
                except Exception as e:
                    print("RSS lỗi", q, off, e, flush=True)
                time.sleep(DELAY)
            print("RSS", q, len(per_query.get(q, [])), flush=True)
        random.seed(7)
        for lst in per_query.values():
            random.shuffle(lst)
        # Xen kẽ theo từ khóa để mỗi phong cách đều có mặt
        candidates, i = [], 0
        while any(i < len(v) for v in per_query.values()):
            candidates += [v[i] for v in per_query.values() if i < len(v)]
            i += 1
        json.dump(candidates, open(cand_path, "w", encoding="utf-8"), ensure_ascii=False)
    print("CANDIDATES", len(candidates), flush=True)

    kept_path, log_path = os.path.join(DATA, "kept.jsonl"), os.path.join(DATA, "excluded.jsonl")
    done = set()
    for p in (kept_path, log_path):
        if os.path.exists(p):
            done |= {json.loads(l)["id"] for l in open(p, encoding="utf-8")}
    kept = sum(1 for _ in open(kept_path, encoding="utf-8")) if os.path.exists(kept_path) else 0
    for it in candidates:
        if kept >= TARGET:
            break
        if it["id"] in done:
            continue
        try:
            flags = page_flags(it["url"], it["id"])
        except Exception as e:
            flags = {"found": False, "noaiMeta": False, "isAiUseDisallowed": False, "isAiGenerated": False, "isMature": False}
            print("trang lỗi", it["url"], e, flush=True)
        time.sleep(DELAY)
        why = exclusion(it, flags)
        if why:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"id": it["id"], "query": it["query"], "reason": why}, ensure_ascii=False) + "\n")
            continue
        thumb = os.path.join(THUMBS, f"{it['id']}.jpg")
        try:
            open(thumb, "wb").write(fetch(it["thumb"], binary=True))
            it["palette"] = palette(thumb)
        except Exception as e:
            print("ảnh lỗi", it["id"], e, flush=True)
            continue
        with open(kept_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
        kept += 1
        if kept % 50 == 0:
            print("KEPT", kept, flush=True)
    print("DONE kept", kept, flush=True)


if __name__ == "__main__":
    main()
