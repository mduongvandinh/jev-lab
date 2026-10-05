"""Lồng tiếng cho video mô phỏng bằng VieNeu (giọng của skill repo-video), phụ đề căn theo từng câu.

Chạy bằng python có cài vieneu (cần TTS_SCRIPTS, xem lab/config.py)
Đọc lời từ out/narration.json {cảnh: "lời đọc"}, ghi viz/public/audio/<cảnh>.m4a và viz/src/data/narration.json.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from config import get  # noqa: E402

sys.path.insert(0, get("TTS_SCRIPTS", ""))
from tts import build_scene, split_sentences  # noqa: E402
from vieneu import Vieneu  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    lines = json.load(open(os.path.join(ROOT, "out", "narration.json"), encoding="utf-8"))
    tts = Vieneu()
    out_dir = os.path.join(ROOT, "viz", "public", "audio")
    os.makedirs(out_dir, exist_ok=True)
    result = {}
    for scene, text in lines.items():
        with tempfile.TemporaryDirectory() as work:
            caps, secs = build_scene(tts, split_sentences(text), os.path.join(out_dir, f"{scene}.m4a"), work)
        result[scene] = {"audio": f"audio/{scene}.m4a", "seconds": secs, "captions": caps}
        print("NARR", scene, secs, flush=True)
    json.dump(result, open(os.path.join(ROOT, "viz", "src", "data", "narration.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
