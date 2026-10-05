"""Lồng tiếng một tập bằng VieNeu (giọng của skill repo-video), phụ đề theo từng câu.

Chạy bằng python có cài vieneu: python lab/narrate.py <slug> (cần TTS_SCRIPTS, xem lab/config.py)
Đọc episodes/<slug>/narration.json {cảnh: lời}, ghi viz/public/<slug>/<cảnh>.m4a và episodes/<slug>/voice.json.
Chỉ đọc lại cảnh có lời thay đổi.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get  # noqa: E402

sys.path.insert(0, get("TTS_SCRIPTS", ""))
from tts import build_scene, split_sentences  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    slug = sys.argv[1]
    ep = os.path.join(ROOT, "episodes", slug)
    lines = json.load(open(os.path.join(ep, "narration.json"), encoding="utf-8"))
    voice_path = os.path.join(ep, "voice.json")
    old = json.load(open(voice_path, encoding="utf-8")) if os.path.exists(voice_path) else {}
    out_dir = os.path.join(ROOT, "viz", "public", slug)
    os.makedirs(out_dir, exist_ok=True)
    tts, result = None, {}
    for scene, text in lines.items():
        audio = os.path.join(out_dir, f"{scene}.m4a")
        if old.get(scene, {}).get("text") == text and os.path.exists(audio):
            result[scene] = old[scene]
            continue
        if tts is None:
            from vieneu import Vieneu
            tts = Vieneu()
        with tempfile.TemporaryDirectory() as work:
            caps, secs = build_scene(tts, split_sentences(text), audio, work)
        result[scene] = {"text": text, "audio": f"{slug}/{scene}.m4a", "seconds": secs, "captions": caps}
        print("NARR", scene, secs, flush=True)
    json.dump(result, open(voice_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
