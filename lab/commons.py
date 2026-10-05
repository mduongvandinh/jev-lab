"""Ảnh Wikimedia Commons: chỉ nhận ảnh nằm trên Commons (giấy phép tự do), lấy tác giả + giấy phép (50 file/request) và tải về public/."""
import html
import os
import re
import time
import urllib.parse
import urllib.request

from common import UA, get_json


def is_commons(url):
    return bool(url) and "/wikipedia/commons/" in url


def credits(urls):
    files = {u: urllib.parse.unquote(u.split("/")[-2] if "/thumb/" in u else u.split("/")[-1]) for u in urls if is_commons(u)}
    names, out = list(set(files.values())), {}
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
    return {u: out.get(f.replace("_", " ")) for u, f in files.items()}


def fetch(url, dest):
    if not os.path.exists(dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            open(dest, "wb").write(r.read())
        time.sleep(0.5)
