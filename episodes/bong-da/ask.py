"""Mỗi cú sút một request: Jev chỉ thấy tình huống (không tên cầu thủ/đội, không xG, không kết quả).
goal (Noul): khả năng thành bàn; quality (Score): chất lượng cơ hội; kind (Choice): kiểu cơ hội.
Thêm --consistency: hỏi lại 3 cú sút 15 lần.
Ra: jev/answers.jsonl, jev/consistency.json
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import MODEL, ask_all, read_jsonl  # noqa: E402
from jevcall import decide  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = {"penalty": "Penalty kick", "direct_free_kick": "Direct free kick", "one_on_one": "One-on-one with the goalkeeper",
         "close_range": "Close-range finish inside the six-yard box or near it", "header": "Header, usually from a cross or set piece",
         "box_shot": "Shot from inside the penalty area with defenders around", "long_range": "Long-range shot from outside the box", "tight_angle": "Shot from a tight angle near the byline"}
QUESTIONS = {
    "goal": {"type": "noul", "instructions": "At the FIFA World Cup, will this shot end up as a goal?", "criteria": {"true": "The shot is scored", "false": "The shot is saved, blocked or misses"}},
    "quality": {"type": "score", "instructions": "How good is this scoring chance for an international-level player?",
                "criteria": ["Very poor chance", "Poor chance", "Half chance", "Good chance", "Big chance"]},
    "kind": {"type": "choice", "instructions": "Which kind of chance is this?", "criteria": KINDS},
}


# play_pattern của StatsBomb là cách pha tấn công BẮT ĐẦU, không phải kiểu cú sút (tránh để Jev hiểu nhầm thành sút phạt trực tiếp)
PATTERN = {"From Free Kick": "a free kick earlier in the move (the ball was then played on)", "From Corner": "a corner kick earlier in the move",
           "From Throw In": "a throw-in earlier in the move", "From Counter": "a counter-attack", "Regular Play": "regular build-up play",
           "From Goal Kick": "a goal kick earlier in the move", "From Keeper": "the goalkeeper", "From Kick Off": "a kick-off", "Other": "other"}


def state(s):
    return {"shot_situation": {
        "distance_to_goal_center_m": s["distance_m"], "visible_goal_angle_deg": s["angle_deg"], "defenders_between_ball_and_goal": s["defenders_in_way"],
        "goalkeeper_distance_from_goal_center_m": s["keeper_off_goal_m"], "opponents_within_2_5m_of_shooter": s["opponents_within_2_5m"],
        "body_part": s["body_part"], "technique": s["technique"], "shot_type": s["shot_type"], "first_time_shot": s["first_time"],
        "one_on_one": s["one_on_one"], "under_pressure": s["under_pressure"],
        "shot_type_note": "Direct free-kick shot" if s["shot_type"] == "Free Kick" else "Penalty kick" if s["shot_type"] == "Penalty" else "Shot from open play (not a direct set-piece shot)",
        "attack_started_from": PATTERN.get(s["play_pattern"], s["play_pattern"]), "assist": s["assist"], "minute": s["minute"]}}


def build(s):
    return {"state": state(s), "questions": QUESTIONS}


if __name__ == "__main__":
    shots = read_jsonl(os.path.join(HERE, "data", "shots.jsonl"))
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    if "--test" in sys.argv:
        s = next(x for x in shots if x["player"].startswith("Lionel") and x["shot_type"] == "Open Play")
        print({k: s[k] for k in ("match", "minute", "player", "distance_m", "angle_deg", "defenders_in_way", "xg", "outcome")})
        print(json.dumps(decide({"model": MODEL, **build(s)})["response"], ensure_ascii=False)[:900])
        sys.exit()
    ask_all(shots, build, os.path.join(HERE, "jev", "answers.jsonl"))
    if "--consistency" in sys.argv:
        out = []
        for s in [x for x in shots if x["shot_type"] == "Open Play"][::400][:3]:
            runs = [decide({"model": MODEL, **build(s)})["response"]["answers"]["goal"]["noul"] for _ in range(15)]
            out.append({"id": s["id"], "player": s["player"], "values": runs, "sd": round(statistics.pstdev(runs), 4), "xg": s["xg"]})
            print("CONSIST", out[-1]["player"], out[-1]["sd"], flush=True)
        json.dump(out, open(os.path.join(HERE, "jev", "consistency.json"), "w"), ensure_ascii=False, indent=1)
