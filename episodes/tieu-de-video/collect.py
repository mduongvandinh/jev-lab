"""Lấy video gần đây của các kênh YouTube lớn qua RSS công khai (không cần API key): tiêu đề, lượt xem, ảnh thumbnail.

Bỏ Shorts; chỉ giữ video đăng trước CUTOFF ít nhất MIN_AGE_DAYS ngày để lượt xem kịp ổn định.
Ra: data/videos.jsonl, ../../viz/public/tieu-de-video/thumbs/<id>.jpg
"""
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_text  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
THUMBS = os.path.join(HERE, "..", "..", "viz", "public", "tieu-de-video", "thumbs")
CUTOFF = dt.datetime(2026, 10, 5, tzinfo=dt.timezone.utc)
MIN_AGE_DAYS = 10
HANDLES = ["MrBeast", "veritasium", "mkbhd", "kurzgesagt", "LinusTechTips", "MarkRober", "3blue1brown", "Vsauce", "TomScottGo",
           "smartereveryday", "CGPGrey", "Fireship", "ColdFusion", "johnnyharris", "Vox", "WIRED", "TheVerge", "NileRed", "StuffMadeHere",
           "PracticalEngineeringChannel", "RealEngineering", "Wendoverproductions", "halfasinteresting", "Mrwhosetheboss", "unboxtherapy",
           "TechLinked", "MrBeastGaming", "Insider", "ScienceChannel", "TED", "TEDEd", "economics explained", "BeastReacts", "DougDeMuro",
           "CNBC", "BusinessInsider", "NetworkChuck", "TwoMinutePapers", "ThioJoe", "JerryRigEverything", "Dude Perfect", "Yes Theory",
           "MarquesBrownlie", "Computerphile", "PBSSpaceTime"]
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "m": "http://search.yahoo.com/mrss/"}


def channel_id(handle):
    html = get_text("https://www.youtube.com/@" + handle.replace(" ", ""), headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en"}, tries=2)
    m = re.search(r'"externalId":"(UC[\w-]{22})"', html)
    return m.group(1) if m else None


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    os.makedirs(THUMBS, exist_ok=True)
    seen_ch, rows = set(), []
    for h in HANDLES:
        try:
            cid = channel_id(h)
        except RuntimeError:
            cid = None
        if not cid or cid in seen_ch:
            print("SKIP", h, flush=True)
            continue
        seen_ch.add(cid)
        root = ET.fromstring(get_text(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"))
        ch_name = root.findtext("a:title", namespaces=NS)
        kept = 0
        for e in root.findall("a:entry", NS):
            link = e.find("a:link", NS).get("href")
            pub = dt.datetime.fromisoformat(e.findtext("a:published", namespaces=NS))
            if "/shorts/" in link or (CUTOFF - pub).days < MIN_AGE_DAYS:
                continue
            vid = e.findtext("yt:videoId", namespaces=NS)
            views = int(e.find("m:group/m:community/m:statistics", NS).get("views"))
            thumb = os.path.join(THUMBS, f"{vid}.jpg")
            if not os.path.exists(thumb):
                try:
                    with urllib.request.urlopen(f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg", timeout=30) as r:
                        open(thumb, "wb").write(r.read())
                except Exception as ex:
                    print("thumb lỗi", vid, ex, flush=True)
                    continue
            rows.append({"id": vid, "channel": ch_name, "title": e.findtext("a:title", namespaces=NS), "views": views,
                         "published": pub.isoformat(), "age_days": (CUTOFF - pub).days})
            kept += 1
        print("CH", ch_name, kept, flush=True)
        time.sleep(1.5)
    with open(os.path.join(HERE, "data", "videos.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("VIDEOS", len(rows), "CHANNELS", len(seen_ch))
