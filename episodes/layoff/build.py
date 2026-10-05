"""Tiêu đề tin layoff 2026 (Google News) + chuyện kể sau layoff (Hacker News) -> episode.json.

Tin layoff = Noul is_layoff >= 0,7. Tên công ty: Jev chỉ chọn trong ứng viên regex. Đếm số TIÊU ĐỀ nhắc tới công ty, không phải số người bị cắt
(số trong tiêu đề hay là tổng cả ngành). Số tin mỗi tháng bị giới hạn bởi RSS nên không so xu hướng theo tháng.
"""
import json
import os
import random
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402
from pick import months, names  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SECTOR_VI = {"software_internet": "Phần mềm, Internet", "hardware_semis": "Phần cứng, chip", "finance": "Tài chính", "retail_ecommerce": "Bán lẻ, TMĐT",
             "media_entertainment": "Truyền thông, giải trí", "auto_manufacturing": "Ô tô, sản xuất", "healthcare_pharma": "Y tế, dược", "government_public": "Nhà nước, giáo dục",
             "telecom": "Viễn thông", "energy": "Năng lượng", "logistics_travel": "Vận tải, du lịch", "consulting_services": "Tư vấn", "other": "Khác"}
REASON_VI = {"ai_automation": "AI, tự động hóa", "cost_cutting": "Cắt giảm chi phí", "restructuring": "Tái cấu trúc", "weak_demand": "Bán chậm", "tariffs_trade": "Thuế quan",
             "closure_bankruptcy": "Đóng cửa, phá sản", "merger": "Sáp nhập", "funding_cuts": "Cắt ngân sách", "not_stated": "Không nêu"}
OUT_VI = {"same_field_job": "Việc mới cùng nghề", "different_field_job": "Việc mới khác nghề", "freelance": "Làm tự do", "own_business": "Tự mở công ty",
          "still_searching": "Vẫn đang tìm", "break_retired": "Nghỉ, về hưu", "study": "Đi học lại", "unclear": "Không rõ"}


def vi_time(t):
    w = {"a": "1", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12"}
    n, unit = t.split(" ", 1)
    return f"{w.get(n.lower(), n)} {'tháng' if unit.startswith('month') else 'năm' if unit.startswith('year') else 'tuần'}"


def pick(text, a, key, fn):
    return fn(text)[int(a[key]["choice"][1:])] if key in a and a[key]["choice"] != "none" else None


def main():
    news = {n["id"]: n for n in read_jsonl(os.path.join(HERE, "data", "news.jsonl"))}
    na = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "news.jsonl")) if "answers" in r}
    stories = {s["id"]: s for s in read_jsonl(os.path.join(HERE, "data", "stories.jsonl"))}
    sa = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "stories.jsonl")) if "answers" in r}
    lay = [(news[i], r["answers"]) for i, r in na.items() if r["answers"]["is_layoff"]["noul"] >= 0.7]
    comp = Counter(c for c in (pick(n["title"], a, "company", names) for n, a in lay) if c)
    sector = Counter(a["sector"]["choice"] for n, a in lay if a["sector"]["confidence"] >= 0.6 and a["sector"]["choice"] != "other")
    reason = Counter(a["reason"]["choice"] for n, a in lay if a["reason"]["confidence"] >= 0.6)
    stated = {k: v for k, v in reason.items() if k != "not_stated"}
    country = Counter(a["country"]["choice"] for n, a in lay if a["country"]["confidence"] >= 0.6)
    ai_comp = Counter(c for c in (pick(n["title"], a, "company", names) for n, a in lay if a["reason"]["choice"] == "ai_automation") if c)
    st = [(stories[i], r["answers"]) for i, r in sa.items() if r["answers"]["personal"]["noul"] >= 0.7]
    outc = Counter(a["outcome"]["choice"] for s, a in st if a["outcome"]["confidence"] >= 0.6 and a["outcome"]["choice"] != "unclear")
    mood = {o: statistics.mean(a["mood"]["score"] for s, a in st if a["outcome"]["choice"] == o) for o in outc}
    tt = Counter(t for t in (pick(s["text"], a, "time_to_job", months) for s, a in st) if t)
    spend = cost(list(na.values()) + list(sa.values()))
    random.seed(6)
    sample = random.sample(lay, 140)
    srt = sorted(lay, key=lambda x: x[0]["id"])
    demo_n, demo_a = next((n, a) for n, a in srt if a["reason"]["choice"] == "ai_automation" and pick(n["title"], a, "company", names) and len(n["title"]) < 95)

    def card(n):
        return {"icon": "📰", "title": n["title"], "sub": f"{n['source']} · {n['month'][5:]}/{n['month'][:4]}"}

    top_out = outc.most_common()
    ep = {"slug": "layoff", "title": "Layoff 2026: ai bị cắt, rồi họ làm gì?", "accent": "#f43f5e", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · LAYOFF 2026", "headline": "Layoff 2026: ai bị cắt, rồi họ làm gì?",
         "sub": f"{len(na):,} tiêu đề tin tức và {len(sa)} chuyện kể của người trong cuộc, AI đọc từng cái".replace(",", ".")},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · TIN TỨC", "title": "Mỗi thẻ là một tiêu đề", "cards": [card(n) for n, a in sample], "total": len(na), "totalLabel": "đã đọc",
         "unit": "tiêu đề", "excluded": len(na) - len(lay), "excludedLabel": "không phải tin cắt việc", "cols": 3, "cardH": 170,
         "credit": "Tiêu đề Google News tiếng Anh, tháng 1–10/2026; chỉ dùng tiêu đề, không lấy bài"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · ĐỌC MỘT TIÊU ĐỀ", "title": "Công ty nào, vì sao?", "cookbook": "Parallel questions · Pre-parsed value extraction",
         "idea": "Tên công ty: máy tìm các cụm viết hoa, Jev chỉ được chọn một.", "stateLines": [f"\"{demo_n['title']}\"", f"{demo_n['source']}"],
         "questions": [{"name": "is_layoff", "kind": "Noul", "text": "Có công ty cụ thể cắt việc?"}, {"name": "company", "kind": "Choice", "text": "Công ty nào?"},
                       {"name": "sector", "kind": "Choice", "text": "Ngành gì?"}, {"name": "country", "kind": "Choice", "text": "Nước nào?"}, {"name": "reason", "kind": "Choice", "text": "Lý do?"}],
         "results": [{"name": "is_layoff", "value": f"có: {round(demo_a['is_layoff']['noul'] * 100)}%", "tone": "good"}, {"name": "company", "value": pick(demo_n["title"], demo_a, "company", names)},
                     {"name": "sector", "value": SECTOR_VI[demo_a["sector"]["choice"]]}, {"name": "reason", "value": REASON_VI[demo_a["reason"]["choice"]], "tone": "warn"}]},
        {"type": "bars", "key": "companies", "step": "BƯỚC 3 · CÔNG TY", "title": "Bị nhắc nhiều nhất trong tin layoff",
         "bars": [{"label": c, "value": v, "text": f"{v} tin", "tone": "bad" if i == 0 else "jev"} for i, (c, v) in enumerate(comp.most_common(8))],
         "note": "Số tiêu đề nhắc tới công ty, không phải số người bị cắt."},
        {"type": "bars", "key": "sectors", "step": "BƯỚC 4 · NGÀNH", "title": "Ngành nào cắt nhiều tin nhất",
         "bars": [{"label": SECTOR_VI[s], "value": v, "text": f"{v} tin", "tone": "bad" if i == 0 else "jev"} for i, (s, v) in enumerate(sector.most_common(7))],
         "note": f"Nước được nêu nhiều nhất: Mỹ, {country['us']} tin; Đức {country['germany']}, Anh {country['uk']}."},
        {"type": "bars", "key": "reasons", "step": "BƯỚC 5 · LÝ DO", "title": "Lý do được nêu trong tiêu đề",
         "bars": [{"label": REASON_VI[r], "value": v, "text": f"{round(100 * v / sum(stated.values()))}%", "tone": "warn" if r == "ai_automation" else "jev"} for r, v in sorted(stated.items(), key=lambda kv: -kv[1])[:6]],
         "note": f"Trên {sum(stated.values())} tin có nêu lý do; {reason['not_stated']:,} tin không nêu.".replace(",", ".") + f" Nêu AI nhiều nhất: {', '.join(c for c, _ in ai_comp.most_common(3))}."},
        {"type": "bars", "key": "after", "step": "BƯỚC 6 · SAU KHI BỊ CẮT", "title": "Họ đã làm gì tiếp?",
         "bars": [{"label": OUT_VI[o], "value": v, "text": f"{v} người", "sub": f"tâm trạng {mood[o]:.1f}/4".replace(".", ","), "tone": "good" if mood[o] >= 2.4 else "bad" if mood[o] < 1.6 else "jev"} for o, v in top_out],
         "note": f"{len(st)} người tự kể trên Hacker News; {sum(outc.values())} người nói rõ kết cục. Mốc tìm việc hay được kể nhất: {vi_time(tt.most_common(1)[0][0])} ({sum(tt.values())} người có nêu thời gian)."},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": "AI là lý do được nêu nhiều nhất",
         "tagline": f"{round(100 * stated['ai_automation'] / sum(stated.values()))}% tiêu đề có nêu lý do nhắc tới AI. Người tự mở công ty sau layoff có tâm trạng tốt nhất, người vẫn đang tìm việc tệ nhất.",
         "stats": [{"value": f"{len(lay):,}".replace(",", "."), "label": "tin cắt việc"}, {"value": str(len(st)), "label": "chuyện kể người thật"}, {"value": f"{spend['usd'] * 100:.0f} cent", "label": "tiền gọi Jev"}],
         "bullets": [f"Meta được nhắc trong {comp['Meta']} tiêu đề, nhiều nhất", f"Phần mềm, Internet là ngành bị nhắc nhiều nhất ({sector['software_internet']} tin)",
                     f"Vẫn đang tìm việc: tâm trạng {mood['still_searching']:.1f}/4; tự mở công ty: {mood['own_business']:.1f}/4".replace(".", ",")],
         "footnote": "Tiêu đề báo tiếng Anh, chủ yếu về Mỹ; nhiều bài cho cùng một đợt cắt. Chuyện kể từ cộng đồng lập trình viên, không đại diện mọi người lao động."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"news": len(na), "layoff": len(lay), "companies": comp.most_common(10), "sector": sector.most_common(), "reason": reason.most_common(), "stated": sum(stated.values()),
             "country": country.most_common(6), "ai_companies": ai_comp.most_common(5), "stories": len(sa), "personal": len(st), "outcome": top_out,
             "mood": {k: round(v, 2) for k, v in mood.items()}, "time": tt.most_common(6), "cost": spend, "demo": demo_n["title"]}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False))


if __name__ == "__main__":
    main()
