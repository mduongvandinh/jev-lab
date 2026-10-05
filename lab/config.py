"""Cấu hình máy cục bộ: đọc biến môi trường trước, rồi tới lab/local.json (không đưa lên git).

JEV_CLI       đường dẫn tới jev.py của repo jev-skill (skills/jev/scripts/jev.py)
JEV_ENV_FILE  file .env chứa TYPESAFE_API_KEY=... hoặc JEV_KEY=... (bỏ qua nếu đã đặt biến TYPESAFE_API_KEY)
TTS_SCRIPTS   thư mục có tts.py (build_scene, split_sentences) để lồng tiếng; chỉ cần khi làm video
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_LOCAL = os.path.join(HERE, "local.json")
_local = json.load(open(_LOCAL, encoding="utf-8")) if os.path.exists(_LOCAL) else {}


def get(name, default=None):
    value = os.environ.get(name) or _local.get(name) or default
    return os.path.expanduser(value) if isinstance(value, str) else value
