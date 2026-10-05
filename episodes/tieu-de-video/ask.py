"""Biến mỗi tiêu đề thành các cột số (cookbook Autoresearch feature discovery, bản rút gọn: bộ câu hỏi cố định, không có vòng LLM đề xuất).
Jev chỉ thấy tiêu đề, không thấy tên kênh hay lượt xem. Các đặc điểm đếm được bằng code (số, dấu hỏi, độ dài) thì để code đếm.
Ra: jev/answers.jsonl
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import ask_all, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = ["Not at all", "Slightly", "Moderately", "Strongly", "Extremely"]
FORMATS = {"challenge_stunt": "Challenge, stunt or competition", "product_review": "Product, gadget or tech review", "science_explainer": "Science or math explainer",
           "engineering_build": "Engineering, building or making something", "news_business": "News, business or economics analysis",
           "history_story": "History, geography or true story", "other": "Reaction, vlog or something else"}


def noul(q, t, f):
    return {"type": "noul", "instructions": q, "criteria": {"true": t, "false": f}}


QUESTIONS = {
    "curiosity": {"type": "score", "instructions": "How strongly does this video title create a curiosity gap that makes a viewer want to click to find out?", "criteria": LEVELS},
    "emotion": {"type": "score", "instructions": "How emotionally intense is the title (excitement, fear, outrage, awe)?", "criteria": LEVELS},
    "concrete": {"type": "score", "instructions": "How concrete and specific is the title's promise (a clear object, outcome or scenario)?", "criteria": LEVELS},
    "stakes": noul("Does the title promise extreme stakes or scale (huge money, danger, world records, life-or-death)?", "Extreme stakes or scale", "Ordinary stakes"),
    "personal": noul("Is the title framed as the creator's own action or experience (I/we did, tried, built, spent)?", "First-person action or experience", "Not first-person"),
    "negative": noul("Is the title framed around a problem, danger, failure, mistake or warning?", "Negative or warning framing", "Neutral or positive framing"),
    "explain": noul("Does the title promise to explain how or why something works or happened?", "Promises an explanation", "Does not promise an explanation"),
    "product": noul("Is the title about a specific named product, gadget, company or brand?", "About a specific product or brand", "Not about a specific product or brand"),
    "format": {"type": "choice", "instructions": "Which kind of video does this title suggest?", "criteria": FORMATS},
}


def build(v):
    return {"state": {"youtube_video_title": v["title"]}, "questions": QUESTIONS}


if __name__ == "__main__":
    rows = read_jsonl(os.path.join(HERE, "data", "videos.jsonl"))
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    ask_all(rows, build, os.path.join(HERE, "jev", "answers.jsonl"))
