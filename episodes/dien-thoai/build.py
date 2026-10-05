"""Biến bình luận Hacker News + đáp án Jev thành episode.json cho tập "điện thoại".

Ngưỡng 0,6 kiểu cookbook Self-consistency: choices: nhãn máy/chủ đề có confidence < 0,6 thì ghi "chưa chắc", không tính.
Chê = thái độ < 1,5/4; khen = > 2,5/4. Đổi phe = Noul switched >= 0,7 và hướng có confidence >= 0,6.
"""
import json
import os
import random
import re
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CONF = 0.6
PHONE_VI = {"iphone": "iPhone", "samsung": "Samsung", "pixel": "Pixel", "other_android": "Android hãng khác", "android_general": "Android nói chung",
            "comparison": "So sánh hai bên", "not_phones": "Lạc đề"}
TOPIC_VI = {"battery": "Pin, sạc", "camera": "Camera", "price_value": "Giá", "updates_longevity": "Cập nhật, độ bền phần mềm", "ecosystem": "Hệ sinh thái",
            "privacy_security": "Quyền riêng tư", "size_design": "Kích thước, thiết kế", "performance": "Hiệu năng", "repair_durability": "Sửa chữa, độ bền",
            "ai_features": "Tính năng AI", "software_ux": "Phần mềm, giao diện", "other": "Khác"}
DIR_VI = {"android_to_iphone": "Android → iPhone", "iphone_to_android": "iPhone → Android"}


def snippet(t, n=110):
    t = " ".join(t.split())
    return "“" + (t[:n].rsplit(" ", 1)[0] + "…" if len(t) > n else t) + "”"


def main():
    com = {c["id"]: c for c in read_jsonl(os.path.join(HERE, "data", "comments.jsonl"))}
    res = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "answers.jsonl")) if "answers" in r}
    rows = []
    for i, r in res.items():
        a = r["answers"]
        rows.append({**com[i], "phone": a["phone"]["choice"], "pc": a["phone"]["confidence"], "pp": a["phone"]["probabilities"][a["phone"]["choice"]],
                     "stance": a["stance"]["score"], "topic": a["topic"]["choice"], "tc": a["topic"]["confidence"], "tp": a["topic"]["probabilities"][a["topic"]["choice"]],
                     "sw": a["switched"]["noul"], "dir": a["direction"]["choice"], "dc": a["direction"]["confidence"], "dp": a["direction"]["probabilities"][a["direction"]["choice"]]})
    n = len(rows)
    off = sum(r["phone"] == "not_phones" for r in rows)
    sure = lambda r: r["pc"] >= CONF  # noqa: E731
    phones = ["iphone", "samsung", "pixel"]
    by = {p: [r for r in rows if r["phone"] == p and sure(r)] for p in phones}
    neg = {p: sum(r["stance"] < 1.5 for r in by[p]) / len(by[p]) for p in phones}
    pos = {p: sum(r["stance"] > 2.5 for r in by[p]) / len(by[p]) for p in phones}
    topics = [t for t, _ in Counter(r["topic"] for p in phones for r in by[p] if r["tc"] >= CONF and r["topic"] != "other").most_common(7)]
    share = [[round(100 * sum(r["topic"] == t and r["tc"] >= CONF for r in by[p]) / len(by[p])) for t in topics] for p in phones]
    neg_top = {p: Counter(r["topic"] for r in by[p] if r["tc"] >= CONF and r["stance"] < 1.5 and r["topic"] != "other").most_common(1)[0] for p in phones}
    sw = [r for r in rows if r["sw"] >= 0.7 and r["dir"] != "none" and r["dc"] >= CONF]
    swc = Counter(r["dir"] for r in sw)
    sw_why = {d: Counter(r["topic"] for r in sw if r["dir"] == d and r["tc"] >= CONF and r["topic"] != "other").most_common(3) for d in DIR_VI}
    kb = [r for r in by["iphone"] if r["topic"] == "software_ux" and r["tc"] >= CONF and r["stance"] < 1.5]
    kb_n = sum(bool(re.search(r"\bkeyboard", r["text"].lower())) for r in kb)
    unsure = sum(r["pc"] < CONF or r["tc"] < CONF for r in rows)
    months = sorted(r["created"][:7] for r in rows)
    spend = cost(list(res.values()))

    def card(r, full=False):
        return {"icon": "📱", "title": f"Hacker News · {r['created'][8:10]}/{r['created'][5:7]}/{r['created'][:4]}", "sub": snippet(r["text"], 160 if full else 110)}

    random.seed(3)
    sample = random.sample(rows, 150)
    scan_cards = [{**card(r), "locked": "lạc đề, không nói về điện thoại"} if r["phone"] == "not_phones" else card(r) for r in sample]
    srt = sorted(rows, key=lambda r: r["id"])
    demo = next(r for r in srt if r["sw"] >= 0.9 and r["dir"] == "iphone_to_android" and r["tc"] >= 0.8 and len(r["text"]) < 500)
    ex = [next(r for r in srt[k * 300:] if r["phone"] == p and r["pc"] >= 0.9 and r["tc"] >= 0.7 and len(r["text"]) < 450) for k, p in enumerate(phones)]
    ex.append(next(r for r in srt if r["pc"] >= 0.9 and r["tc"] < 0.45 and r["phone"] in phones and len(r["text"]) < 450))

    def ans(r):
        return [{"q": "Nói về", "text": PHONE_VI[r["phone"]], "prob": r["pp"]},
                {"q": "Thái độ", "text": "chê" if r["stance"] < 1.5 else "khen" if r["stance"] > 2.5 else "trung lập", "tone": "bad" if r["stance"] < 1.5 else "good" if r["stance"] > 2.5 else "muted"},
                {"q": "Chủ đề", "text": TOPIC_VI[r["topic"]] if r["tc"] >= CONF else "chưa chắc", "prob": r["tp"], "tone": "jev" if r["tc"] >= CONF else "warn"}]

    jd = [r for r in sorted(sw, key=lambda r: r["id"]) if len(r["text"]) < 500]
    judge = [next(r for r in jd if r["dir"] == "android_to_iphone"), next(r for r in jd if r["dir"] == "iphone_to_android")]
    judge += [next(r for r in jd[40:] if r["dir"] == "android_to_iphone"), next(r for r in jd[40:] if r["dir"] == "iphone_to_android")]
    judge.append(next(r for r in srt if 0.4 <= r["sw"] < 0.7 and len(r["text"]) < 500))

    ep = {"slug": "dien-thoai", "title": "Dân công nghệ chê iPhone, Samsung, Pixel vì gì?", "accent": "#a855f7", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · ĐIỆN THOẠI", "headline": "Dân công nghệ chê iPhone, Samsung, Pixel vì gì?",
         "sub": f"{n:,} bình luận thật trên Hacker News, AI đọc từng cái".replace(",", ".")},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · DỮ LIỆU THẬT", "title": "Mỗi thẻ là một bình luận", "cards": scan_cards, "total": n, "totalLabel": "đã đọc", "unit": "bình luận",
         "excluded": off, "excludedLabel": "lạc đề", "cols": 3, "cardH": 210, "credit": f"Bình luận công khai trên Hacker News, {months[0][5:7]}/{months[0][:4]}–{months[-1][5:7]}/{months[-1][:4]}, qua API Algolia"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · MỘT LẦN GỌI, NĂM CÂU", "title": "Đọc một bình luận", "cookbook": "Parallel questions",
         "idea": "Năm câu hỏi gộp trong một request cho mỗi bình luận.", "stateLines": [snippet(demo["text"], 150)],
         "questions": [{"name": "phone", "kind": "Choice", "text": "Nói về máy nào?"}, {"name": "stance", "kind": "Score", "text": "Khen hay chê?"},
                       {"name": "topic", "kind": "Choice", "text": "Chuyện gì: pin, camera, giá…?"}, {"name": "switched", "kind": "Noul", "text": "Có đổi phe không?"},
                       {"name": "direction", "kind": "Choice", "text": "Đổi từ đâu sang đâu?"}],
         "results": [{"name": "phone", "value": PHONE_VI[demo["phone"]]}, {"name": "stance", "value": f"{demo['stance']:.1f}/4".replace(".", ","), "tone": "warn"},
                     {"name": "topic", "value": TOPIC_VI[demo["topic"]]}, {"name": "switched", "value": f"có: {round(demo['sw'] * 100)}%", "tone": "good"},
                     {"name": "direction", "value": DIR_VI[demo["dir"]], "tone": "good"}]},
        {"type": "label", "key": "label", "step": "BƯỚC 3 · CHẮC THÌ TÍNH, CHƯA CHẮC THÌ BỎ", "title": "Nhãn nào dưới 60% thì không tính", "cookbook": "Self-consistency: choices",
         "examples": [{"card": card(r), "answers": ans(r)} for r in ex],
         "tally": {"title": "Bình luận nói về máy nào", "bars": [{"label": PHONE_VI[p], "value": sum(1 for r in rows if r["phone"] == p and sure(r))} for p, _ in Counter(r["phone"] for r in rows if r["phone"] != "not_phones").most_common(5)]}},
        {"type": "heat", "key": "heat", "step": "BƯỚC 4 · MỖI MÁY BỊ BÀN CHUYỆN GÌ", "title": "Chủ đề theo từng dòng máy", "rows": [PHONE_VI[p] for p in phones],
         "cols": ["Phần mềm" if t == "software_ux" else TOPIC_VI[t].split(",")[0] for t in topics], "values": share,
         "highlight": [[i, max(range(len(topics)), key=lambda j: share[i][j])] for i in range(3)], "legend": "% bình luận về máy đó nói tới từng chủ đề. Ô viền vàng: nhiều nhất"},
        {"type": "bars", "key": "mood", "step": "BƯỚC 5 · KHEN HAY CHÊ", "title": "Ai được khen nhiều hơn?",
         "bars": [{"label": PHONE_VI[p], "value": pos[p], "text": f"{round(pos[p] * 100)}% khen", "sub": f"{round(neg[p] * 100)}% chê · {len(by[p])} bình luận", "tone": "good" if p == max(phones, key=pos.get) else "jev"} for p in sorted(phones, key=lambda p: -pos[p])],
         "note": f"Chê nhiều nhất: iPhone vì {TOPIC_VI[neg_top['iphone'][0]].lower()}, Samsung vì {TOPIC_VI[neg_top['samsung'][0]].lower()}, Pixel vì {TOPIC_VI[neg_top['pixel'][0]].lower()}."},
        {"type": "judge", "key": "judge", "step": "BƯỚC 6 · AI ĐỔI PHE?", "title": "Đọc chuyện người đổi máy",
         "items": [{"card": card(r, True), "pass": r["sw"] >= 0.7, "stamp": DIR_VI[r["dir"]].upper() if (r["sw"] >= 0.7 and r["dir"] in DIR_VI and r["dc"] >= CONF) else "CHƯA CHẮC",
                    "metrics": [{"label": "Có đổi phe", "value": r["sw"], "text": f"{round(r['sw'] * 100)}%", "tone": "good"},
                                {"label": "Chắc về hướng", "value": r["dc"], "text": f"{r['dc']:.2f}".replace(".", ","), "tone": "jev"}]} for r in judge]},
        {"type": "bars", "key": "switch", "step": "BƯỚC 7 · KẾT QUẢ ĐỔI PHE", "title": f"{len(sw)} người kể chuyện đổi máy",
         "bars": [{"label": DIR_VI[d], "value": swc[d], "text": f"{swc[d]} người", "sub": "vì " + ", ".join(TOPIC_VI[t].lower() for t, _ in sw_why[d][:2]), "tone": "good" if d == swc.most_common(1)[0][0] else "jev"} for d in DIR_VI],
         "note": "Truy vấn tìm cả hai chiều với số lượng như nhau, nhưng đây là người kể trên Hacker News, không phải số liệu bán hàng."},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": f"{PHONE_VI[max(phones, key=pos.get)]} được khen nhiều nhất",
         "tagline": f"iPhone bị bàn nhiều nhất, và bị chê nhiều nhất vì phần mềm: khoảng {round(100 * kb_n / len(kb))}% lời chê đó nhắc tới bàn phím.",
         "stats": [{"value": f"{n:,}".replace(",", "."), "label": "bình luận đã đọc"}, {"value": f"{off}", "label": "lạc đề, Jev tự lọc"}, {"value": f"{spend['usd'] * 100:.0f} cent", "label": "tiền gọi Jev"}],
         "bullets": [f"Đổi phe: {swc['android_to_iphone']} người sang iPhone, {swc['iphone_to_android']} người sang Android",
                     f"Pixel được bàn nhiều nhất về quyền riêng tư",
                     f"{unsure:,} bình luận có nhãn dưới 60% chắc chắn, không tính".replace(",", ".")],
         "footnote": "Hacker News là cộng đồng lập trình viên, chủ yếu nói tiếng Anh, không đại diện cho mọi người dùng. Bình luận lấy theo từ khóa, mới nhất trước."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"n": n, "off": off, "by": {p: len(by[p]) for p in phones}, "pos": {p: round(pos[p], 3) for p in phones}, "neg": {p: round(neg[p], 3) for p in phones},
             "topics": topics, "share": dict(zip(phones, share)), "neg_top": neg_top, "switch": dict(swc), "sw_why": sw_why, "kb": [kb_n, len(kb)], "unsure": unsure,
             "months": [months[0], months[-1]], "cost": spend, "demo": {k: demo[k] for k in ("text", "phone", "stance", "topic", "sw", "dir")},
             "examples": [(PHONE_VI[r["phone"]], r["topic"], round(r["tc"], 2), round(r["stance"], 2)) for r in ex], "judge": [(r["dir"], round(r["sw"], 2), round(r["dc"], 2)) for r in judge]}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in facts.items() if k != "demo"}, ensure_ascii=False)); print(facts["demo"]["text"][:300])


if __name__ == "__main__":
    main()
