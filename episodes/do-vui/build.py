"""Đố vui lịch sử -> episode.json. So BM25 (chỉ từ khóa) với BM25 + Jev xếp lại; câu bẫy: Jev có biết nói "không có" không.

Đúng = đoạn đứng đầu thuộc bài của vị vua đáp án (questions.json: gold). Câu bẫy đúng khi điểm cao nhất < 0,5.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402
from ask import sentences  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    P = {p["id"]: p for p in read_jsonl(os.path.join(HERE, "data", "paragraphs.jsonl"))}
    Q = json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))
    B = json.load(open(os.path.join(HERE, "data", "bm25.json")))
    R = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "rerank.jsonl")) if "answers" in r}
    L = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "lines.jsonl")) if "answers" in r}
    res = {}
    for q in Q:
        c = [P[p] for p in B[q["id"]]]
        sc = [R[q["id"]]["answers"][f"p{j}"]["noul"] for j in range(len(c))]
        order = sorted(range(len(c)), key=lambda j: -sc[j])
        best = c[order[0]]
        line = None
        if q["id"] in L:
            ch = L[q["id"]]["answers"]["line"]["choice"]
            line = sentences(best["text"])[int(ch[1:])] if ch != "none" else None
        g = set(q["gold"])
        res[q["id"]] = {"q": q["q"], "trap": not g, "bm_top": c[0]["king"], "bm_ok": c[0]["king_id"] in g, "jev_top": best["king"], "jev_ok": best["king_id"] in g,
                        "bm_rank": next((j + 1 for j, x in enumerate(c) if x["king_id"] in g), None), "score": sc[order[0]], "line": line,
                        "gold": [P[p]["king"] for p in B[q["id"]] if P[p]["king_id"] in g][:1]}
    real = [r for r in res.values() if not r["trap"]]
    traps = [r for r in res.values() if r["trap"]]
    bm, jv = sum(r["bm_ok"] for r in real), sum(r["jev_ok"] for r in real)
    trap_ok = sum(r["score"] < 0.5 for r in traps)
    spend = cost(list(R.values()) + list(L.values()))
    random.seed(5)
    sample = random.sample(list(P.values()), 120)

    def short(t, n=150):
        t = " ".join(t.split())
        return t[:n].rsplit(" ", 1)[0] + "…" if len(t) > n else t

    picks = ["q4", "q2", "q11", "q20", "t2"]
    items = []
    for k in picks:
        r = res[k]
        if r["trap"]:
            items.append({"card": {"icon": "❓", "title": r["q"], "sub": f"Từ khóa vẫn trả về một đoạn về {r['bm_top']}", "lines": ["Jev: không đoạn nào trả lời"]},
                          "pass": r["score"] < 0.5, "stamp": "KHÔNG CÓ ĐÁP ÁN",
                          "metrics": [{"label": "Điểm cao nhất của Jev", "value": r["score"], "text": f"{round(r['score'] * 100)}%", "tone": "bad"}]})
        else:
            items.append({"card": {"icon": "❓", "title": r["q"], "sub": short(r["line"] or "", 130), "lines": [f"Từ khóa xếp đầu: {r['bm_top']}"]},
                          "pass": r["jev_ok"], "stamp": f"JEV: {r['jev_top'].upper()}",
                          "metrics": [{"label": "Jev chấm đoạn đứng đầu", "value": r["score"], "text": f"{round(r['score'] * 100)}%", "tone": "good"},
                                      {"label": "Từ khóa xếp đáp án", "value": 1 / (r["bm_rank"] or 30), "text": f"hạng {r['bm_rank']}", "tone": "muted"}]})
    q4 = res["q4"]
    cands = [P[p] for p in B["q4"]]
    sc4 = R["q4"]["answers"]
    top3 = sorted(range(len(cands)), key=lambda j: -sc4[f"p{j}"]["noul"])[:3]
    ep = {"slug": "do-vui", "title": "Đố vui lịch sử: AI tìm đáp án trong Wikipedia", "accent": "#14b8a6", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · ĐỐ VUI", "headline": "Đố AI: vua nào đổi quốc hiệu thành Đại Việt?",
         "sub": f"24 câu đố lịch sử, đáp án nằm đâu đó trong {len(P):,} đoạn văn Wikipedia. Có cả 4 câu bẫy".replace(",", ".")},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · KHO TÀI LIỆU", "title": "99 bài về các vua Việt Nam", "cards": [{"icon": "📜", "title": p["king"], "sub": short(p["text"], 110)} for p in sample],
         "total": len(P), "totalLabel": "đã chia", "unit": "đoạn văn", "cols": 3, "cardH": 200, "credit": "Toàn văn bài về 99 vị vua trên Wikipedia tiếng Việt (CC BY-SA)"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · TÌM RỒI XẾP LẠI", "title": "Từ khóa tìm nhanh, Jev xếp lại", "cookbook": "Re-ranking · Parallel questions",
         "idea": "Từ khóa lấy 30 đoạn ứng viên. Jev hỏi 30 câu trong một lần gọi: đoạn này có trả lời không?",
         "stateLines": [f"Câu hỏi: {q4['q']}", f"Từ khóa xếp đầu: {q4['bm_top']} · đáp án ở hạng {q4['bm_rank']}"],
         "questions": [{"name": f"p{j}", "kind": "Noul", "text": f"Đoạn về {cands[j]['king']}"} for j in top3],
         "results": [{"name": f"p{j}", "value": f"{round(sc4[f'p{j}']['noul'] * 100)}%", "tone": "good" if k == 0 else "muted"} for k, j in enumerate(top3)],
         "footer": f"Jev đưa đoạn về {q4['jev_top']} lên đầu: \"{short(q4['line'] or '', 90)}\""},
        {"type": "judge", "key": "judge", "step": "BƯỚC 3 · TỪNG CÂU ĐỐ", "title": "Câu trả lời nằm ở dòng nào?", "cookbook": "Line-by-line search", "items": items},
        {"type": "bars", "key": "score", "step": "BƯỚC 4 · CHẤM ĐIỂM", "title": "Ai trả lời đúng hơn?",
         "bars": [{"label": "Chỉ tìm từ khóa", "value": bm / len(real), "text": f"{bm}/{len(real)}", "sub": "đoạn đứng đầu đúng bài", "tone": "muted"},
                  {"label": "Từ khóa + Jev xếp lại", "value": jv / len(real), "text": f"{jv}/{len(real)}", "sub": "đoạn đứng đầu đúng bài", "tone": "good"},
                  {"label": "Câu bẫy: biết nói không có", "value": trap_ok / len(traps), "text": f"{trap_ok}/{len(traps)}", "sub": "từ khóa thì luôn trả về một đoạn", "tone": "warn"}],
         "note": "Câu sai duy nhất của Jev (đánh Tống năm 981) vẫn chỉ đúng câu \"Lê Hoàn đánh bại quân Tống\", chỉ là nằm trong bài của vua khác."},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": f"{jv}/{len(real)} câu đúng, {trap_ok}/{len(traps)} câu bẫy",
         "tagline": "Tìm từ khóa thì nhanh nhưng hay chọn nhầm đoạn. Jev xếp lại thì đúng hơn, và biết nói không có khi tài liệu không có đáp án.",
         "stats": [{"value": f"{len(P):,}".replace(",", "."), "label": "đoạn văn"}, {"value": "24", "label": "câu đố"}, {"value": f"{spend['usd'] * 100:.1f} cent".replace(".", ","), "label": "tiền gọi Jev"}],
         "bullets": [], "gridTitle": "Vài câu đố và đáp án Jev tìm được", "gridCols": 1,
         "grid": [{"label": res[k]["q"][:38] + ("…" if len(res[k]["q"]) > 38 else ""), "value": res[k]["jev_top"]} for k in ("q1", "q5", "q7", "q17", "q19")],
         "footnote": "20 câu đố có đáp án và 4 câu bẫy do mình đặt; kho tài liệu chỉ gồm 99 bài về các vua. BM25 là cách tìm từ khóa đơn giản."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"paragraphs": len(P), "real": len(real), "bm25_top1": bm, "jev_top1": jv, "traps": len(traps), "trap_ok": trap_ok,
             "trap_scores": [round(r["score"], 2) for r in traps], "cost": spend, "results": res}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({k: v for k, v in facts.items() if k != "results"})


if __name__ == "__main__":
    main()
