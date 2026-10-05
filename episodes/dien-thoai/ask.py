"""Mỗi bình luận một request, 5 câu (Parallel questions): phone (Choice), stance (Score), topic (Choice), switched (Noul), direction (Choice).
Bỏ bình luận từ truy vấn "grapheneos pixel" để Pixel không lệch hẳn về chủ đề quyền riêng tư.
Ra: jev/answers.jsonl
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import MODEL, ask_all, read_jsonl  # noqa: E402
from jevcall import decide  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PHONES = {"iphone": "Apple iPhone / iOS", "samsung": "Samsung Galaxy phones", "pixel": "Google Pixel phones", "other_android": "Another Android brand (Xiaomi, OnePlus, Motorola...)",
          "android_general": "Android in general, no specific brand", "comparison": "Mainly compares iPhone and Android equally", "not_phones": "Not really about smartphones"}
TOPICS = {"battery": "Battery life or charging", "camera": "Camera and photos", "price_value": "Price or value for money", "updates_longevity": "Software updates, support length, how long the phone lasts",
          "ecosystem": "Ecosystem and lock-in (iMessage, watch, laptop integration)", "privacy_security": "Privacy and security", "size_design": "Size, weight or design",
          "performance": "Speed and performance", "repair_durability": "Repairability, durability, breaking", "ai_features": "AI features or assistants",
          "software_ux": "Software, UI, bugs, bloatware, customization", "other": "Something else"}
QUESTIONS = {
    "phone": {"type": "choice", "instructions": "Which phone or platform is this comment mainly about?", "criteria": PHONES},
    "stance": {"type": "score", "instructions": "What is the commenter's attitude toward that phone or platform?", "criteria": ["Very negative", "Negative", "Mixed or neutral", "Positive", "Very positive"]},
    "topic": {"type": "choice", "instructions": "What aspect of the phone does the comment mainly discuss?", "criteria": TOPICS},
    "switched": {"type": "noul", "instructions": "Does the commenter say they personally switched, or are switching, between iPhone and Android?",
                 "criteria": {"true": "They personally switched or are switching platforms", "false": "No personal platform switch mentioned"}},
    "direction": {"type": "choice", "instructions": "If the commenter personally switched platforms, in which direction?",
                  "criteria": {"android_to_iphone": "From Android to iPhone", "iphone_to_android": "From iPhone to Android", "none": "No personal switch, or unclear"}},
}


def build(c):
    return {"state": {"hacker_news_comment": c["text"][:2000], "thread_title": c.get("story") or ""}, "questions": QUESTIONS}


if __name__ == "__main__":
    rows = [r for r in read_jsonl(os.path.join(HERE, "data", "comments.jsonl")) if r["query"] != "grapheneos pixel"]
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    if "--test" in sys.argv:
        c = next(r for r in rows if "switched" in r["text"].lower() and "iphone" in r["text"].lower())
        print(c["text"][:400])
        a = decide({"model": MODEL, **build(c)})["response"]
        print({k: (v.get("choice") or v.get("score") or v.get("noul"), v.get("confidence")) for k, v in a["answers"].items()}, a["usage"])
        sys.exit()
    print("ROWS", len(rows))
    ask_all(rows, build, os.path.join(HERE, "jev", "answers.jsonl"))
