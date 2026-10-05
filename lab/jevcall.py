"""Gọi Jev thật qua CLI của repo jev-skill (provider TypeSafe).

Key lấy từ biến TYPESAFE_API_KEY, hoặc từ file JEV_ENV_FILE (dòng TYPESAFE_API_KEY=... hoặc JEV_KEY=...).
Key chỉ được đưa vào biến môi trường của tiến trình con; không in, không ghi ra file.
Dùng như module: decide(request_dict) -> response dict;  hoặc: python3 jevcall.py request.json
"""
import json
import os
import re
import subprocess
import sys
import tempfile

from config import get

JEV_CLI = get("JEV_CLI")


def _key():
    if os.environ.get("TYPESAFE_API_KEY"):
        return os.environ["TYPESAFE_API_KEY"]
    path = get("JEV_ENV_FILE")
    if path and os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            m = re.match(r"\s*(?:export\s+)?(?:TYPESAFE_API_KEY|JEV_KEY)\s*=\s*(.*)$", line)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    raise SystemExit("Thiếu key: đặt TYPESAFE_API_KEY hoặc JEV_ENV_FILE (xem lab/config.py)")


def decide(request, timeout=120):
    if not JEV_CLI or not os.path.exists(JEV_CLI):
        raise SystemExit("Thiếu JEV_CLI: trỏ tới skills/jev/scripts/jev.py của repo jev-skill (xem lab/config.py)")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(request, f, ensure_ascii=False)
        path = f.name
    try:
        env = {**os.environ, "TYPESAFE_API_KEY": _key()}
        res = subprocess.run([sys.executable, JEV_CLI, "decide", "--provider", "typesafe", "--timeout", str(timeout), path],
                             capture_output=True, text=True, env=env, timeout=timeout + 30)
    finally:
        os.remove(path)
    # CLI: exit 0 = mọi quyết định đạt ngưỡng; exit 2 = có quyết định cần xem lại nhưng vẫn trả đủ kết quả
    if res.returncode in (0, 2):
        try:
            out = json.loads(res.stdout)
            if "response" in out:
                return out
        except json.JSONDecodeError:
            pass
    raise RuntimeError(f"Jev lỗi (exit {res.returncode}): {(res.stderr or res.stdout).strip()[-400:]}")


if __name__ == "__main__":
    print(json.dumps(decide(json.load(open(sys.argv[1], encoding="utf-8"))), ensure_ascii=False, indent=1))
