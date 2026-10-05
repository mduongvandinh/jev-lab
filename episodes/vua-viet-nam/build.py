"""99 vua Việt Nam (nhà Ngô 939 – nhà Nguyễn 1945) -> episode.json.

Năm trị vì: từ bảng của bài "Vua Việt Nam". Năm sinh / mất: Jev chọn trong các năm regex tìm được (khớp 74/74 với ngày ghi trong ngoặc đầu bài).
"""
import json
import os
import re
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from commons import credits, fetch, is_commons  # noqa: E402
from common import cost, read_jsonl  # noqa: E402
from ask import years  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "..", "..", "viz", "public", "vua-viet-nam")
CAME_VI = {"son": "Nối ngôi cha", "installed": "Được quyền thần, triều đình lập", "relative": "Nối ngôi anh, chú, họ hàng", "founded": "Lập triều đại mới",
           "usurped": "Cướp ngôi", "foreign": "Ngoại bang dựng lên", "unclear": "Không rõ"}
END_VI = {"died_on_throne": "Mất khi đang trị vì", "deposed": "Bị phế truất", "killed": "Bị giết, bức tử", "abdicated": "Tự nhường ngôi",
          "war_fall": "Mất nước trong chiến tranh", "captured_exiled": "Bị bắt, lưu đày", "unclear": "Không rõ"}
MAIN = ["Nhà Lý", "Nhà Trần", "Lê sơ", "Nhà Mạc", "Lê trung hưng", "Nhà Nguyễn"]
ENDS = ["died_on_throne", "deposed", "killed", "abdicated"]


def clean(name):
    return re.sub(r"(?<=[a-zà-ỹ])(?=[A-ZĐ])", " / ", name)


def main():
    K = {k["id"]: k for k in read_jsonl(os.path.join(HERE, "data", "kings.jsonl"))}
    res = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "answers.jsonl")) if "answers" in r}
    rows = []
    for i, r in res.items():
        k, a = K[i], r["answers"]
        c = years(k["extract"][:2000])
        yr = lambda key: int(c[int(a[key]["choice"][1:])]) if key in a and a[key]["choice"] != "none" else None  # noqa: E731
        rs = re.findall(r"\d{3,4}", k["reign_text"])
        rows.append({**k, "name": clean(k["name"]), "born": yr("born"), "died": yr("died"), "start": int(rs[0]) if rs else None, "end": int(rs[-1]) if rs else None,
                     "came": a["came"]["choice"], "ended": a["ended"]["choice"], "legacy": a["legacy"]["score"], "a": a, "years": c})
    reign = [r for r in rows if r["start"] and r["end"]]
    longest = max(reign, key=lambda r: r["end"] - r["start"])
    acc = [r for r in rows if r["born"] and r["start"] and 0 <= r["start"] - r["born"] < 90]
    youngest = min(acc, key=lambda r: r["start"] - r["born"])
    life = [r for r in rows if r["born"] and r["died"] and 0 < r["died"] - r["born"] < 100]
    oldest, shortest = max(life, key=lambda r: r["died"] - r["born"]), min(life, key=lambda r: r["died"] - r["born"])
    came, ended = Counter(r["came"] for r in rows), Counter(r["ended"] for r in rows)
    heat = [[sum(1 for r in rows if r["dynasty"] == d and r["ended"] == e) for e in ENDS] for d in MAIN]
    spend = cost(list(res.values()))
    thumbs = [r["thumb"] for r in rows if is_commons(r.get("thumb"))]
    cred = credits(thumbs)

    def card(r):
        c = {"title": r["name"], "sub": f"{r['dynasty']} · {r['reign_text']}"}
        if is_commons(r.get("thumb")) and cred.get(r["thumb"]):
            fetch(r["thumb"], os.path.join(PUB, f"{r['id']}.jpg"))
            c.update({"img": f"vua-viet-nam/{r['id']}.jpg", "credit": cred[r["thumb"]]})
        else:
            c["icon"] = "👑"
        return c

    demo = next(r for r in rows if r["name"] == "Tiền Ngô Vương")
    da = demo["a"]
    by_legacy = sorted(rows, key=lambda r: -r["legacy"])
    rec = [("Trị vì lâu nhất", longest, f"{longest['end'] - longest['start']} năm", f"{longest['start']}–{longest['end']}"),
           ("Lên ngôi nhỏ tuổi nhất", youngest, f"{youngest['start'] - youngest['born']} tuổi", f"sinh {youngest['born']}, lên ngôi {youngest['start']}"),
           ("Sống thọ nhất", oldest, f"{oldest['died'] - oldest['born']} tuổi", f"{oldest['born']}–{oldest['died']}"),
           ("Mất sớm nhất", shortest, f"{shortest['died'] - shortest['born']} tuổi", f"{shortest['born']}–{shortest['died']}")]
    ep = {"slug": "vua-viet-nam", "title": "99 vua Việt Nam qua những con số", "accent": "#d97706", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · LỊCH SỬ", "headline": "99 vị vua Việt Nam qua những con số",
         "sub": "Từ Ngô Quyền năm 939 tới Bảo Đại năm 1945. AI đọc bài Wikipedia của từng vị vua"},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · DỮ LIỆU", "title": "Mỗi thẻ là một vị vua", "cards": [card(r) for r in rows], "total": len(rows), "totalLabel": "đã đọc",
         "unit": "vị vua", "cols": 3, "cardH": 230, "credit": "Bài \"Vua Việt Nam\" và bài riêng từng vua trên Wikipedia tiếng Việt (CC BY-SA). Ảnh: Wikimedia Commons"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · ĐỌC NGÀY THÁNG", "title": "Sinh năm nào, mất năm nào?", "cookbook": "Date extraction · Pre-parsed value extraction",
         "idea": "Máy tìm mọi con số năm trong bài, Jev chỉ được chọn. Ghi \"?\" thì Jev trả lời không rõ.",
         "stateLines": [demo["extract"][:140].replace("\n", " ") + "…", "Các năm tìm được: " + ", ".join(demo["years"][:6])],
         "questions": [{"name": "born", "kind": "Choice", "text": "Năm sinh?"}, {"name": "died", "kind": "Choice", "text": "Năm mất?"},
                       {"name": "came", "kind": "Choice", "text": "Lên ngôi bằng cách nào?"}, {"name": "ended", "kind": "Choice", "text": "Rời ngôi thế nào?"},
                       {"name": "legacy", "kind": "Score", "text": "Sử sách đánh giá ra sao?"}],
         "results": [{"name": "born", "value": str(demo["born"]), "tone": "good"}, {"name": "died", "value": str(demo["died"]), "tone": "good"},
                     {"name": "came", "value": CAME_VI[da["came"]["choice"]]}, {"name": "ended", "value": END_VI[da["ended"]["choice"]]},
                     {"name": "legacy", "value": f"{da['legacy']['score']:.1f}/4".replace(".", ","), "tone": "warn"}],
         "footer": "Kiểm tra: năm Jev chọn khớp 74/74 với ngày ghi trong ngoặc đầu bài"},
        {"type": "bars", "key": "came", "step": "BƯỚC 3 · LÊN NGÔI", "title": "Lên ngôi bằng cách nào?",
         "bars": [{"label": CAME_VI[k], "value": v, "text": f"{v} vị", "tone": "good" if i == 0 else "jev"} for i, (k, v) in enumerate(came.most_common()) if k != "unclear"]},
        {"type": "bars", "key": "ended", "step": "BƯỚC 4 · RỜI NGÔI", "title": "Kết cục của 99 vị vua",
         "bars": [{"label": END_VI[k], "value": v, "text": f"{v} vị", "tone": "bad" if k in ("killed", "deposed") else "good" if k == "died_on_throne" else "jev"} for k, v in ended.most_common() if k != "unclear"],
         "note": f"{ended['unclear']} vị bài viết không nói rõ."},
        {"type": "heat", "key": "dyn", "step": "BƯỚC 5 · THEO TRIỀU ĐẠI", "title": "Mỗi triều một kiểu kết thúc", "rows": MAIN, "cols": ["Mất tại vị", "Bị phế", "Bị giết", "Nhường ngôi"],
         "values": heat, "highlight": [[1, 3], [2, 1]], "legend": "Số vị vua. Nhà Trần nổi bật với tục nhường ngôi làm Thái thượng hoàng."},
        {"type": "columns", "key": "reigns", "step": "BƯỚC 6 · THỜI GIAN TRỊ VÌ", "title": "Mỗi cột là một vị vua",
         "cols": [{"label": "", "value": r["end"] - r["start"], "color": "#d97706" if r is longest else "#92400e", "highlight": r is longest} for r in sorted(reign, key=lambda r: r["start"])],
         "note": f"Theo thứ tự thời gian, từ 939 tới 1945. Trung vị chỉ {statistics.median(r['end'] - r['start'] for r in reign):.0f} năm; cao nhất là {longest['name']}."},
        {"type": "timeline", "key": "records", "step": "BƯỚC 7 · KỶ LỤC", "title": "Những con số đặc biệt",
         "items": [{"years": lab, "title": r["name"], "sub": f"{r['dynasty']} · {note}", "stat": val, **({k: card(r)[k] for k in ("img", "credit")} if card(r).get("img") else {})} for lab, r, val, note in rec]},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": f"Cứ 8 vị vua, 1 vị bị giết",
         "tagline": f"{ended['killed']} trong 99 vị bị giết hoặc bức tử, {ended['deposed']} vị bị phế. Hơn một nửa nối ngôi cha, và thời gian trị vì trung vị chỉ {statistics.median(r['end'] - r['start'] for r in reign):.0f} năm.",
         "stats": [{"value": "99", "label": "vị vua"}, {"value": "74/74", "label": "năm sinh, mất khớp nguồn"}, {"value": f"{spend['usd'] * 100:.1f} cent".replace(".", ","), "label": "tiền gọi Jev"}],
         "bullets": [], "gridTitle": "Được bài viết đánh giá cao nhất", "gridCols": 1,
         "grid": [{"label": r["name"], "value": f"{r['legacy']:.1f}/4".replace(".", ",")} for r in by_legacy[:5]],
         "footnote": "Năm trị vì theo bảng của bài \"Vua Việt Nam\" (bài riêng có thể ghi lệch 1 năm). Đánh giá là cách văn bản Wikipedia mô tả triều đại, không phải phán xét của Jev."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"n": len(rows), "came": came.most_common(), "ended": ended.most_common(), "median_reign": statistics.median(r["end"] - r["start"] for r in reign),
             "records": [(lab, r["name"], val) for lab, r, val, _ in rec], "heat": dict(zip(MAIN, heat)), "legacy_top": [(r["name"], round(r["legacy"], 2)) for r in by_legacy[:5]],
             "legacy_low": [(r["name"], round(r["legacy"], 2)) for r in by_legacy[-5:]], "cost": spend, "images": sum(1 for r in rows if is_commons(r.get("thumb")))}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False))


if __name__ == "__main__":
    main()
