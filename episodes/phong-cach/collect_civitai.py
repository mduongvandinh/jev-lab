"""Thu thập ảnh từ API công khai của Civitai (không cần tài khoản), chỉ ảnh an toàn (PG), tải ảnh 300px, đo bảng màu.

Lưu ý: mọi ảnh trên Civitai đều do AI tạo — bản đồ phong cách phản ánh cộng đồng AI art.
Lịch sự: giãn cách 3 giây, tự chờ khi API báo quá tải; lưu sau mỗi trang để chạy tiếp được.
Dùng: python3 collect_civitai.py [số ảnh, mặc định 1000]
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from collect import palette  # dùng chung hàm đo bảng màu

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
THUMBS = os.path.join(ROOT, "thumbs")
UA = {"User-Agent": "style-gap research script (public API, PG only)"}
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
DELAY = 3

# Trộn nhiều cách sắp xếp để bản đồ phong cách không lệch về một gu
FEEDS = [("Most Reactions", "Week"), ("Most Reactions", "Month"), ("Most Reactions", "Year"),
         ("Most Comments", "Month"), ("Newest", "AllTime")]
PER_FEED = TARGET // len(FEEDS) + 20


def get_json(url):
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            if "items" in data:
                return data
            print("API:", str(data)[:120], flush=True)
        except Exception as e:
            print("lỗi mạng:", e, flush=True)
        time.sleep(20 * (attempt + 1))  # quá tải: chờ lâu dần
    raise RuntimeError("Civitai không phản hồi sau nhiều lần thử")


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(THUMBS, exist_ok=True)
    kept_path = os.path.join(DATA, "kept.jsonl")
    state_path = os.path.join(DATA, "civitai_state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    seen = {json.loads(l)["id"] for l in open(kept_path, encoding="utf-8")} if os.path.exists(kept_path) else set()
    for sort, period in FEEDS:
        key = f"{sort}|{period}"
        feed = state.setdefault(key, {"cursor": None, "count": 0})
        while feed["count"] < PER_FEED and len(seen) < TARGET and feed["cursor"] != "END":
            q = {"limit": 50, "sort": sort, "period": period, "nsfw": "None"}
            if feed["cursor"]:
                q["cursor"] = feed["cursor"]
            data = get_json("https://civitai.com/api/v1/images?" + urllib.parse.urlencode(q))
            for it in data["items"]:
                rid = f"civ{it['id']}"
                safe = it.get("nsfw") is False and it.get("browsingLevel") in (1, None) and it.get("nsfwLevel") in ("None", None)
                if rid in seen or not safe or it.get("type") not in ("image", None):
                    continue
                thumb = os.path.join(THUMBS, f"{rid}.jpg")
                try:
                    with urllib.request.urlopen(urllib.request.Request(it["url"].replace("original=true", "width=300"), headers=UA), timeout=60) as r:
                        open(thumb, "wb").write(r.read())
                    pal = palette(thumb)
                except Exception as e:
                    print("ảnh lỗi", rid, e, flush=True)
                    continue
                rec = {"id": rid, "source": "civitai", "url": f"https://civitai.com/images/{it['id']}", "author": it.get("username"),
                       "baseModel": it.get("baseModel"), "reactions": (it.get("stats") or {}).get("heartCount"),
                       "feed": key, "palette": pal, "width": it.get("width"), "height": it.get("height")}
                with open(kept_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                seen.add(rid)
                feed["count"] += 1
                time.sleep(0.3)
            feed["cursor"] = (data.get("metadata") or {}).get("nextCursor") or "END"
            json.dump(state, open(state_path, "w"), indent=1)
            print("FEED", key, feed["count"], "TOTAL", len(seen), flush=True)
            time.sleep(DELAY)
    print("DONE kept", len(seen), flush=True)


if __name__ == "__main__":
    main()
