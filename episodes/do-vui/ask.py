"""Đố vui lịch sử: tìm đáp án trong 5.095 đoạn của 99 bài Wikipedia về các vua.

1) BM25 (tìm theo từ khóa, âm tiết + cặp âm tiết) lấy TOP_K đoạn ứng viên cho mỗi câu hỏi.
2) Re-ranking: một request mỗi câu hỏi, gộp TOP_K câu Noul "đoạn pN có trả lời câu hỏi không?" (Parallel questions).
3) Line-by-line search: trong đoạn Jev chấm cao nhất, Jev CHỌN câu trả lời (Choice trên từng câu + none).
   Câu bẫy: nếu không đoạn nào đạt 0,5 thì trả lời "không có trong dữ liệu".
Ra: jev/rerank.jsonl, jev/lines.jsonl, data/bm25.json
"""
import json
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import ask_all, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP_K = 30


def tokens(t):
    w = re.findall(r"\w+", t.lower())
    return w + [a + "_" + b for a, b in zip(w, w[1:])]


def bm25(paras, query, k1=1.5, b=0.75):
    docs = [tokens(p["text"]) for p in paras]
    N, avg = len(docs), sum(map(len, docs)) / len(docs)
    df = Counter(t for d in docs for t in set(d))
    q = tokens(query)
    out = []
    for p, d in zip(paras, docs):
        tf, s = Counter(d), 0.0
        for t in q:
            if tf[t]:
                idf = math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
                s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avg))
        out.append(s)
    return [paras[i] for i in sorted(range(N), key=lambda i: -out[i])[:TOP_K]]


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?;])\s+", t) if len(s.split()) >= 4][:60]


def build_rerank(item):
    return {"state": {"question": item["q"], **{f"p{j}": c["text"][:900] for j, c in enumerate(item["cands"])}},
            "questions": {f"p{j}": {"type": "noul", "instructions": f"Does passage p{j} directly answer the question?",
                                    "criteria": {"true": f"Passage p{j} states the answer", "false": f"Passage p{j} does not answer it (only related or off-topic)"}}
                          for j in range(len(item["cands"]))}}


def build_line(item):
    lines = sentences(item["best"]["text"])
    return {"state": {"question": item["q"], **{f"s{j}": s for j, s in enumerate(lines)}},
            "questions": {"line": {"type": "choice", "instructions": "Which sentence answers the question? Choose none if no sentence answers it.",
                                   "criteria": {**{f"s{j}": f"Sentence s{j}" for j in range(len(lines))}, "none": "No sentence answers the question"}}}}


if __name__ == "__main__":
    paras = read_jsonl(os.path.join(HERE, "data", "paragraphs.jsonl"))
    qs = json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))
    items = [{**q, "cands": bm25(paras, q["q"])} for q in qs]
    json.dump({it["id"]: [c["id"] for c in it["cands"]] for it in items}, open(os.path.join(HERE, "data", "bm25.json"), "w"))
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    rr = ask_all(items, build_rerank, os.path.join(HERE, "jev", "rerank.jsonl"), workers=4)
    line_items = []
    for it in items:
        a = rr[it["id"]]["answers"]
        j = max(range(len(it["cands"])), key=lambda j: a[f"p{j}"]["noul"])
        if a[f"p{j}"]["noul"] >= 0.5:
            line_items.append({**it, "best": it["cands"][j]})
    ask_all(line_items, build_line, os.path.join(HERE, "jev", "lines.jsonl"), workers=4)
