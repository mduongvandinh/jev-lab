"""Tin tuyển dụng (Who is hiring) và hồ sơ tìm việc (Who wants to be hired) trên Hacker News -> episode.json.

Bỏ tháng 10/2026 khi so theo tháng (bài mới đăng được vài ngày). Nhãn Choice có confidence < 0,6 không tính.
Lương: Jev chỉ chọn trong các số tiền regex tìm được; chỉ tính tin ghi bằng $ (đa số là USD), 30k–900k/năm.
"""
import json
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402
from pick import money  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROLE_VI = {"backend": "Backend", "frontend": "Frontend", "fullstack": "Full-stack", "mobile": "Mobile", "ml_ai": "ML / AI", "data": "Data",
           "devops_infra": "DevOps, hạ tầng", "security": "Bảo mật", "embedded_hardware": "Nhúng, phần cứng", "design_product": "Sản phẩm, thiết kế",
           "leadership": "Quản lý kỹ thuật", "other": "Nhiều vị trí"}
REGION_VI = {"us": "Mỹ", "europe": "Châu Âu", "anywhere": "Từ xa toàn cầu", "uk": "Anh", "canada": "Canada", "india": "Ấn Độ", "latam": "Mỹ Latinh",
             "asia_other": "Châu Á khác", "africa_me": "Châu Phi, Trung Đông", "oceania": "Úc, NZ", "unclear": "Không ghi"}


def pct(x):
    return f"{round(x * 100)}%"


def k(v):
    return f"{round(v / 1000)}k $"


def parse_money(s):
    vals = []
    for n, u in re.findall(r"(\d+(?:\.\d+)?)\s*([kKmM]?)", s.replace(",", "")):
        v = float(n) * (1000 if u.lower() == "k" else 1e6 if u.lower() == "m" else 1)
        vals.append(v * 1000 if v < 1000 else v)
    return vals


def main():
    posts = {p["id"]: p for p in read_jsonl(os.path.join(HERE, "data", "posts.jsonl"))}
    res = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "answers.jsonl")) if "answers" in r}
    ok = lambda a, q: a[q].get("confidence", 1) >= 0.6  # noqa: E731
    H = [(posts[i], r["answers"]) for i, r in res.items() if posts[i]["kind"] == "hiring"]
    S = [(posts[i], r["answers"]) for i, r in res.items() if posts[i]["kind"] == "seeking"]
    months = sorted({p["month"] for p, _ in H if p["month"] < "2026-10"})
    per = {m: (sum(p["month"] == m for p, _ in H), sum(p["month"] == m for p, _ in S)) for m in months}
    ratio = {m: s / h for m, (h, s) in per.items()}
    rem_h = Counter(a["remote"]["choice"] for p, a in H if ok(a, "remote"))
    rem_s = Counter(a["remote"]["choice"] for p, a in S if ok(a, "remote"))
    nh, ns = sum(rem_h.values()), sum(rem_s.values())
    roles = ["fullstack", "backend", "ml_ai", "devops_infra", "frontend", "data", "leadership", "design_product"]
    rh = Counter(a["role"]["choice"] for p, a in H if ok(a, "role"))
    rs = Counter(a["role"]["choice"] for p, a in S if ok(a, "role"))
    lv_h = Counter(a["level"]["choice"] for p, a in H if ok(a, "level"))
    lv_s = Counter(a["level"]["choice"] for p, a in S if ok(a, "level"))
    sal = []
    for p, a in H:
        if "salary_low" not in a or a["salary_low"]["choice"] == "none":
            continue
        c = money(p["text"])
        lo = c[int(a["salary_low"]["choice"][1:])]
        hi = c[int(a["salary_high"]["choice"][1:])] if a.get("salary_high", {}).get("choice", "none") != "none" else lo
        if "$" not in lo:
            continue
        vl, vh = parse_money(lo), parse_money(hi)
        if vl and 30000 <= min(vl) <= 600000 and max(vh or vl) <= 900000:
            sal.append((p, a, min(vl), max(vh or vl)))
    mid = lambda s: (s[2] + s[3]) / 2  # noqa: E731
    by_role = {r: [mid(s) for s in sal if s[1]["role"]["choice"] == r] for r in ROLE_VI}
    role_pay = sorted([(r, statistics.median(v), len(v)) for r, v in by_role.items() if len(v) >= 10 and r != "other"], key=lambda x: -x[1])
    ai_pay = {b: statistics.median([mid(s) for s in sal if (s[1]["ai_skill"]["noul"] >= 0.5) == b]) for b in (True, False)}
    ai_h = sum(a["ai_skill"]["noul"] >= 0.5 for p, a in H) / len(H)
    ai_s = sum(a["ai_skill"]["noul"] >= 0.5 for p, a in S) / len(S)
    ai_prod = sum(a["ai_product"]["noul"] >= 0.5 for p, a in H) / len(H)
    visa = sum(a["visa"]["noul"] >= 0.5 for p, a in H) / len(H)
    us = sum(a["region"]["choice"] == "us" for p, a in H if ok(a, "region")) / sum(1 for p, a in H if ok(a, "region"))
    spend = cost(list(res.values()))
    first = months[0]
    last = months[-1]

    def card(p):
        line = p["text"].split("\n")[0]
        return {"icon": "💼" if p["kind"] == "hiring" else "🙋", "title": (line[:70] + "…") if len(line) > 70 else line,
                "sub": f"{'Tuyển dụng' if p['kind'] == 'hiring' else 'Tìm việc'} · {p['month'][5:]}/{p['month'][:4]}"}

    random.seed(2)
    sample = random.sample([p for p, _ in H + S], 140)
    demo_p, demo_a, dlo, dhi = next(s for s in sorted(sal, key=lambda s: s[0]["id"]) if s[1]["role"]["choice"] == "ml_ai" and s[3] > s[2] and len(s[0]["text"]) < 700)
    ep = {"slug": "tuyen-dung", "title": "Năm 2026, công ty tuyển dev đòi gì?", "accent": "#0ea5e9", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · VIỆC LÀM 2026", "headline": "Cứ 1 tin tuyển dev, có 2 người tìm việc",
         "sub": f"{len(res):,} tin tuyển dụng và hồ sơ tìm việc trên Hacker News trong 13 tháng, AI đọc từng cái".replace(",", ".")},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · DỮ LIỆU THẬT", "title": "Tin tuyển và hồ sơ tìm việc", "cards": [card(p) for p in sample],
         "total": len(res), "totalLabel": "đã đọc", "unit": "bài", "cols": 3, "cardH": 170, "credit": "Chuỗi bài hằng tháng \"Who is hiring\" và \"Who wants to be hired\" trên Hacker News, 10/2025–10/2026"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · MỘT LẦN GỌI, TÁM CÂU", "title": "Đọc một tin tuyển dụng", "cookbook": "Parallel questions · Pre-parsed value extraction",
         "idea": "Lương thì Jev chỉ được chọn trong các con số có sẵn trong tin, không tự gõ.",
         "stateLines": [demo_p["text"].split("\n")[0][:90], "Ứng viên lương: " + ", ".join(money(demo_p["text"])[:3])],
         "questions": [{"name": "role", "kind": "Choice", "text": "Tuyển vị trí gì?"}, {"name": "remote", "kind": "Choice", "text": "Từ xa, hybrid hay tại chỗ?"},
                       {"name": "ai_skill", "kind": "Noul", "text": "Có đòi kinh nghiệm AI?"}, {"name": "visa", "kind": "Noul", "text": "Có bảo lãnh visa?"},
                       {"name": "salary_low", "kind": "Choice", "text": "Lương thấp nhất?"}, {"name": "salary_high", "kind": "Choice", "text": "Lương cao nhất?"}],
         "results": [{"name": "role", "value": ROLE_VI[demo_a["role"]["choice"]]}, {"name": "remote", "value": {"remote": "Từ xa", "hybrid": "Hybrid", "onsite": "Tại chỗ", "unclear": "Không ghi"}[demo_a["remote"]["choice"]]},
                     {"name": "ai_skill", "value": f"có: {round(demo_a['ai_skill']['noul'] * 100)}%", "tone": "warn"}, {"name": "visa", "value": f"có: {round(demo_a['visa']['noul'] * 100)}%", "tone": "muted"},
                     {"name": "salary", "value": f"{k(dlo)} – {k(dhi)}", "tone": "good"}],
         "footer": "+ 2 câu nữa: khu vực và cấp bậc"},
        {"type": "columns", "key": "ratio", "step": "BƯỚC 3 · CUNG VÀ CẦU", "title": "Người tìm việc trên 100 tin tuyển",
         "cols": [{"label": m[5:], "value": round(ratio[m] * 100), "color": "#0ea5e9", "highlight": m == max(ratio, key=ratio.get)} for m in months],
         "note": f"Tháng {first[5:]}/{first[:4]}: {round(ratio[first] * 100)} người / 100 tin. Tháng {last[5:]}/{last[:4]}: {round(ratio[last] * 100)}. Nhãn là tháng (10 = 10/2025 … 09 = 9/2026)."},
        {"type": "bars", "key": "remote", "step": "BƯỚC 4 · LÀM TỪ XA", "title": "Ai cũng muốn từ xa, tin thì không",
         "bars": [{"label": "Người tìm việc muốn từ xa", "value": rem_s["remote"] / ns, "text": pct(rem_s["remote"] / ns), "tone": "warn"},
                  {"label": "Tin cho làm từ xa hẳn", "value": rem_h["remote"] / nh, "text": pct(rem_h["remote"] / nh), "tone": "good"},
                  {"label": "Tin hybrid", "value": rem_h["hybrid"] / nh, "text": pct(rem_h["hybrid"] / nh), "tone": "jev"},
                  {"label": "Tin chỉ tại chỗ", "value": rem_h["onsite"] / nh, "text": pct(rem_h["onsite"] / nh), "tone": "bad"}],
         "note": "Chỉ tính bài có nhãn chắc chắn từ 0,6."},
        {"type": "heat", "key": "roles", "step": "BƯỚC 5 · VỊ TRÍ", "title": "Tuyển gì và ai đang tìm", "rows": [ROLE_VI[r] for r in roles], "cols": ["Tin tuyển", "Tìm việc"],
         "values": [[round(100 * rh[r] / sum(rh.values())), round(100 * rs[r] / sum(rs.values()))] for r in roles], "highlight": [[roles.index("ml_ai"), 0], [0, 1]],
         "legend": "% số bài thuộc từng vị trí. Cột trái: tin tuyển, cột phải: hồ sơ tìm việc."},
        {"type": "bars", "key": "pay", "step": "BƯỚC 6 · LƯƠNG", "title": "Lương trung vị theo vị trí",
         "bars": [{"label": ROLE_VI[r], "value": v, "text": k(v), "sub": f"{n} tin", "tone": "good" if i == 0 else "jev"} for i, (r, v, n) in enumerate(role_pay)],
         "note": f"{len(sal)} tin có lương bằng $, lấy điểm giữa khoảng lương. Trung vị chung {k(statistics.median(s[2] for s in sal))} – {k(statistics.median(s[3] for s in sal))}."},
        {"type": "bars", "key": "ai", "step": "BƯỚC 7 · AI", "title": "AI có làm lương cao hơn?",
         "bars": [{"label": "Hồ sơ tìm việc có AI", "value": ai_s, "text": pct(ai_s), "tone": "warn"}, {"label": "Công ty làm sản phẩm AI", "value": ai_prod, "text": pct(ai_prod)},
                  {"label": "Tin đòi kinh nghiệm AI", "value": ai_h, "text": pct(ai_h), "tone": "good"}],
         "note": f"Lương trung vị: tin đòi AI {k(ai_pay[True])}, tin không đòi {k(ai_pay[False])}. Gần như không chênh."},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": f"{round(ratio[last] * 100)} người cho 100 tin",
         "tagline": f"Từ {round(ratio[first] * 100)} lên {round(ratio[last] * 100)} trong một năm. Người tìm việc muốn làm từ xa, còn chưa tới một nửa số tin cho phép.",
         "stats": [{"value": f"{len(H):,}".replace(",", "."), "label": "tin tuyển dụng"}, {"value": f"{len(S):,}".replace(",", "."), "label": "hồ sơ tìm việc"},
                   {"value": f"{spend['usd']:.2f} USD".replace(".", ","), "label": "tiền gọi Jev"}],
         "bullets": [f"Tin cho người mới: {pct(lv_h['junior'] / sum(lv_h.values()))}, người mới đi tìm: {pct(lv_s['junior'] / sum(lv_s.values()))}",
                     f"Chỉ {pct(visa)} tin bảo lãnh visa; {pct(us)} tin ở Mỹ", f"ML / AI trả cao nhất: trung vị {k(role_pay[0][1])}" if role_pay[0][0] == "ml_ai" else f"Trả cao nhất: {ROLE_VI[role_pay[0][0]]} {k(role_pay[0][1])}"],
         "footnote": "Hacker News nghiêng về startup công nghệ Mỹ; một người có thể đăng nhiều tháng. Không tính tháng 10/2026 khi so theo tháng."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"hiring": len(H), "seeking": len(S), "per_month": per, "ratio": {m: round(v, 2) for m, v in ratio.items()}, "remote_h": dict(rem_h), "remote_s": dict(rem_s),
             "roles_h": dict(rh), "roles_s": dict(rs), "level_h": dict(lv_h), "level_s": dict(lv_s), "salary_n": len(sal), "role_pay": role_pay, "ai_pay": ai_pay,
             "ai_h": round(ai_h, 3), "ai_s": round(ai_s, 3), "ai_prod": round(ai_prod, 3), "visa": round(visa, 3), "us": round(us, 3), "cost": spend,
             "demo": {"line": demo_p["text"].split("\n")[0], "lo": dlo, "hi": dhi, "role": demo_a["role"]["choice"]}}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(facts, ensure_ascii=False, default=str)[:2500])


if __name__ == "__main__":
    main()
