"""Công ty mới và công ty đóng cửa năm 2026.
1) Y Combinator: mọi công ty các đợt W26, P26, S26, F26 (API công khai), kèm logo.
2) Tiêu đề Google News RSS theo tháng 1–10/2026 về phá sản / đóng cửa công ty.
Ra: data/yc.jsonl, data/closures.jsonl, ../../viz/public/cong-ty/logos/<slug>.png
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json, get_text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOGOS = os.path.join(HERE, "..", "..", "viz", "public", "cong-ty", "logos")
BATCHES = ["Winter 2026", "Spring 2026", "Summer 2026", "Fall 2026"]
CLOSE_Q = ["files for bankruptcy", "company shuts down", "startup shutting down"]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    os.makedirs(LOGOS, exist_ok=True)
    yc = []
    for b in BATCHES:
        url = "https://api.ycombinator.com/v0.1/companies?" + urllib.parse.urlencode({"batch": b})
        while url:
            d = get_json(url)
            for c in d["companies"]:
                logo = os.path.join(LOGOS, f"{c['slug']}.png")
                if c.get("smallLogoUrl") and not os.path.exists(logo):
                    try:
                        with urllib.request.urlopen(c["smallLogoUrl"], timeout=30) as r:
                            open(logo, "wb").write(r.read())
                    except Exception:
                        pass
                yc.append({"id": c["slug"], "name": c["name"], "batch": c["batch"], "oneLiner": c.get("oneLiner"), "description": (c.get("longDescription") or "")[:800],
                           "tags": c.get("tags"), "industries": c.get("industries"), "regions": c.get("regions"), "locations": c.get("locations"),
                           "teamSize": c.get("teamSize"), "logo": os.path.exists(logo)})
            url = d.get("nextPage")
            time.sleep(0.5)
        print("YC", b, len(yc), flush=True)
    closures, seen = [], set()
    for m in range(1, 11):
        a, b = f"2026-{m:02d}-01", f"2026-{m + 1:02d}-01"
        for q in CLOSE_Q:
            root = ET.fromstring(get_text("https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": f"{q} after:{a} before:{b}", "hl": "en-US", "gl": "US", "ceid": "US:en"})))
            for it in root.iter("item"):
                title = it.findtext("title") or ""
                key = re.sub(r"\W+", " ", title.lower())[:90]
                if key not in seen:
                    seen.add(key)
                    closures.append({"id": f"c{len(closures)}", "month": a[:7], "title": title.rsplit(" - ", 1)[0], "source": it.findtext("source") or ""})
            time.sleep(2)
        print("CLOSE", a[:7], len(closures), flush=True)
    for name, rows in (("yc", yc), ("closures", closures)):
        with open(os.path.join(HERE, "data", f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("DONE yc", len(yc), "closures", len(closures))
