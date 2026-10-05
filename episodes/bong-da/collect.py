"""Tải dữ liệu mở của StatsBomb (World Cup 2022): mọi cú sút trong 64 trận, kèm vị trí cầu thủ lúc sút (freeze frame).

Nguồn: https://github.com/statsbomb/open-data (miễn phí, ghi nguồn StatsBomb). Bỏ loạt sút luân lưu (period 5).
Ra: data/shots.jsonl (có xG của StatsBomb và kết quả thật; hai trường này KHÔNG gửi cho Jev)
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
COMP, SEASON = 43, 106


def geometry(x, y, frame):
    """Khoảng cách (m) và góc nhìn khung thành (độ); số hậu vệ trong tam giác bóng–hai cột dọc; thủ môn có đứng đúng chỗ không."""
    yd = 0.9144  # sân StatsBomb tính bằng yard
    dist = math.hypot(120 - x, 40 - y) * yd
    a1, a2 = math.atan2(36 - y, 120 - x), math.atan2(44 - y, 120 - x)
    angle = abs(math.degrees(a2 - a1))

    def inside(px, py):
        def side(ax, ay, bx, by):
            return (bx - ax) * (py - ay) - (by - ay) * (px - ax)
        d1, d2, d3 = side(x, y, 120, 36), side(120, 36, 120, 44), side(120, 44, x, y)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))

    blockers = sum(1 for p in frame or [] if not p["teammate"] and p.get("position", {}).get("name") != "Goalkeeper" and inside(*p["location"]))
    gk = next((p for p in frame or [] if not p["teammate"] and p.get("position", {}).get("name") == "Goalkeeper"), None)
    gk_off = round(math.hypot(gk["location"][0] - 120, gk["location"][1] - 40) * yd, 1) if gk else None
    near = sum(1 for p in frame or [] if not p["teammate"] and math.hypot(p["location"][0] - x, p["location"][1] - y) * yd < 2.5)
    return round(dist, 1), round(angle, 1), blockers, gk_off, near


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    matches = get_json(f"{RAW}/matches/{COMP}/{SEASON}.json")
    rows = []
    for m in matches:
        ev = get_json(f"{RAW}/events/{m['match_id']}.json")
        by_id = {e["id"]: e for e in ev}
        for e in ev:
            if e["type"]["name"] != "Shot" or e["period"] == 5:
                continue
            s = e["shot"]
            x, y = e["location"][:2]
            dist, angle, blockers, gk_off, near = geometry(x, y, s.get("freeze_frame"))
            kp = by_id.get(s.get("key_pass_id"), {}).get("pass", {})
            assist = "cross" if kp.get("cross") else "through ball" if kp.get("through_ball") else "cut-back" if kp.get("cut_back") else ("pass" if kp else "no assist (own play, rebound or set piece)")
            rows.append({"id": e["id"], "match": f"{m['home_team']['home_team_name']} – {m['away_team']['away_team_name']}", "stage": m["competition_stage"]["name"],
                         "minute": e["minute"], "team": e["team"]["name"], "player": e["player"]["name"], "x": x, "y": y,
                         "distance_m": dist, "angle_deg": angle, "defenders_in_way": blockers, "keeper_off_goal_m": gk_off, "opponents_within_2_5m": near,
                         "body_part": s["body_part"]["name"], "technique": s["technique"]["name"], "shot_type": s["type"]["name"],
                         "first_time": bool(s.get("first_time")), "one_on_one": bool(s.get("one_on_one")), "under_pressure": bool(e.get("under_pressure")),
                         "play_pattern": e["play_pattern"]["name"], "assist": assist, "xg": s["statsbomb_xg"], "goal": s["outcome"]["name"] == "Goal",
                         "outcome": s["outcome"]["name"]})
        print("MATCH", m["match_id"], len(rows), flush=True)
        time.sleep(0.3)
    with open(os.path.join(HERE, "data", "shots.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("SHOTS", len(rows), "GOALS", sum(r["goal"] for r in rows))
