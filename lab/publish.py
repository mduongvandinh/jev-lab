"""Gom episode.json + voice.json của mọi tập vào viz/src/data/episodes.json để Remotion đăng ký composition.

Chạy: python3 lab/publish.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    out = {}
    for ep in sorted(glob.glob(os.path.join(ROOT, "episodes", "*", "episode.json"))):
        d = os.path.dirname(ep)
        voice = os.path.join(d, "voice.json")
        out[os.path.basename(d)] = {"episode": json.load(open(ep, encoding="utf-8")),
                                    "voice": json.load(open(voice, encoding="utf-8")) if os.path.exists(voice) else {}}
    os.makedirs(os.path.join(ROOT, "viz", "src", "data"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "viz", "src", "data", "episodes.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("PUBLISHED", ", ".join(out))
