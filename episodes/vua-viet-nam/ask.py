"""Mỗi vua một request (Parallel questions).

Date extraction + Pre-parsed value extraction: regex tìm mọi năm (3–4 chữ số) trong đoạn mở đầu bài viết; Jev chỉ CHỌN năm sinh, năm mất
(hoặc "none" khi bài ghi "?" / không rõ). came / ended: Choice; legacy: Score (cách bài viết đánh giá triều đại).
Ra: jev/answers.jsonl
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import ask_all, read_jsonl  # noqa: E402
from pick import choice  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CAME = {"founded": "Founded a new dynasty or seized power to start one", "son": "Succeeded his father", "relative": "Succeeded a brother, uncle or other relative",
        "installed": "Put on the throne by a regent, powerful official, lord or court faction", "usurped": "Took the throne by coup or overthrowing the ruler",
        "foreign": "Installed or backed by a foreign power", "unclear": "Unclear"}
ENDED = {"died_on_throne": "Died of natural causes while reigning", "killed": "Killed, poisoned or forced to suicide", "abdicated": "Abdicated voluntarily (often to his son, becoming retired emperor)",
         "deposed": "Deposed, forced to abdicate or overthrown", "captured_exiled": "Captured or exiled", "war_fall": "Dynasty fell in war while he reigned", "unclear": "Unclear"}
YEAR = re.compile(r"(?<!\d)(\d{3,4})(?!\d)")


def years(text):
    return list(dict.fromkeys(m.group(1) for m in YEAR.finditer(text) if 800 <= int(m.group(1)) <= 2000))[:24]


def build(k):
    text = k["extract"][:2000]
    q = {"came": {"type": "choice", "instructions": "How did this Vietnamese monarch come to the throne?", "criteria": CAME},
         "ended": {"type": "choice", "instructions": "How did his (or her) reign end?", "criteria": ENDED},
         "legacy": {"type": "score", "instructions": "How positively does the text portray this ruler's reign?", "criteria": ["Very negatively", "Negatively", "Mixed or neutral", "Positively", "Very positively"]}}
    c = years(text)
    for key, instr in (("born", "Which quoted year is the monarch's BIRTH year? Choose none if the birth year is unknown (written as ?)."),
                       ("died", "Which quoted year is the monarch's DEATH year? Choose none if unknown.")):
        ch = choice(instr, c)
        if ch:
            q[key] = ch
    return {"state": {"monarch": k["name"], "dynasty": k["dynasty"], "reign_years_from_table": k["reign_text"], "lineage": k["lineage"], "wikipedia_intro_vi": text},
            "questions": q}


if __name__ == "__main__":
    rows = read_jsonl(os.path.join(HERE, "data", "kings.jsonl"))
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    ask_all(rows, build, os.path.join(HERE, "jev", "answers.jsonl"), workers=6)
