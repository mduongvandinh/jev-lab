"""Công ty mới (Y Combinator 2026) và công ty đóng cửa (tiêu đề Google News 1–10/2026) -> episode.json.

Đóng cửa = Noul is_closure >= 0,7; tên công ty Jev chỉ chọn trong ứng viên regex. Bỏ tên gắn với thảm kịch (trại hè sau lũ) khỏi danh sách hiển thị.
"""
import json
import os
import random
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402
from pick import names  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "layoff"))
from build import SECTOR_VI  # noqa: E402

AREA_VI = {"ai_agents_automation": "AI agent, tự động hóa", "devtools": "Công cụ lập trình", "health": "Y tế", "fintech": "Tài chính", "defense_hardware": "Quốc phòng, phần cứng",
           "robotics": "Robot", "consumer": "App tiêu dùng", "vertical_saas": "Phần mềm ngành", "climate_energy": "Khí hậu, năng lượng", "security": "Bảo mật", "education": "Giáo dục", "other": "Khác"}
JOB_VI = {"customer_support": "Chăm sóc khách hàng", "sales": "Bán hàng", "software_engineering": "Lập trình, kiểm thử", "legal": "Pháp lý", "accounting_finance": "Kế toán",
          "recruiting_hr": "Tuyển dụng, nhân sự", "healthcare_admin": "Hành chính y tế", "data_analysis": "Phân tích dữ liệu", "manual_labor": "Lao động chân tay", "other": "Khác", "none": "Không"}
REASON_VI = {"debt_cash": "Nợ, cạn tiền", "weak_demand": "Bán chậm", "competition": "Thua cạnh tranh", "fraud_legal": "Gian lận, kiện tụng", "tariffs_costs": "Thuế quan, chi phí",
             "funding": "Không gọi được vốn", "acquired": "Bị mua lại", "regulation": "Quy định", "not_stated": "Không nêu"}
SKIP = {"Camp Mystic"}


def pick(text, a, key):
    return names(text)[int(a[key]["choice"][1:])] if key in a and a[key]["choice"] != "none" else None


def main():
    yc = {c["id"]: c for c in read_jsonl(os.path.join(HERE, "data", "yc.jsonl"))}
    ya = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "yc.jsonl")) if "answers" in r}
    cl = {c["id"]: c for c in read_jsonl(os.path.join(HERE, "data", "closures.jsonl"))}
    ca = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "closures.jsonl")) if "answers" in r}
    Y = [(yc[i], r["answers"]) for i, r in ya.items()]
    ai = sum(a["ai_core"]["noul"] >= 0.5 for c, a in Y) / len(Y)
    auto = [(c, a) for c, a in Y if a["automates"]["noul"] >= 0.5]
    area = Counter(a["area"]["choice"] for c, a in Y if a["area"]["confidence"] >= 0.6 and a["area"]["choice"] != "other")
    jobs = Counter(a["job"]["choice"] for c, a in auto if a["job"]["confidence"] >= 0.6 and a["job"]["choice"] not in ("other", "none"))
    sf = sum(1 for c, a in Y if (c["locations"] or [""])[0] == "San Francisco") / len(Y)
    team = statistics.median(int(c["teamSize"]) for c, a in Y if str(c["teamSize"]).isdigit())
    C = [(cl[i], r["answers"]) for i, r in ca.items() if r["answers"]["is_closure"]["noul"] >= 0.7]
    comp = Counter(c for c in (pick(n["title"], a, "company") for n, a in C) if c and c not in SKIP)
    sector = Counter(a["sector"]["choice"] for n, a in C if a["sector"]["confidence"] >= 0.6 and a["sector"]["choice"] != "other")
    reason = Counter(a["reason"]["choice"] for n, a in C if a["reason"]["confidence"] >= 0.6)
    stated = {k: v for k, v in reason.items() if k != "not_stated"}
    spend = cost(list(ya.values()) + list(ca.values()))
    random.seed(8)
    sample = random.sample([c for c, a in Y if c["logo"]], 120)
    demo, da = next((c, a) for c, a in sorted(Y, key=lambda x: x[0]["id"]) if a["automates"]["noul"] > 0.9 and a["job"]["choice"] == "legal")

    def card(c):
        return {"img": f"cong-ty/logos/{c['id']}.png", "fit": "contain", "title": c["name"], "credit": f"YC {c['batch']}"}

    ep = {"slug": "cong-ty", "title": "Công ty mới và công ty đóng cửa 2026", "accent": "#f59e0b", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · CÔNG TY 2026", "headline": "Startup mới đang thay việc của ai?",
         "sub": f"{len(Y)} startup Y Combinator 2026 và {len(ca):,} tin công ty đóng cửa, AI đọc từng cái".replace(",", ".")},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · CÔNG TY MỚI", "title": f"{len(Y)} startup Y Combinator 2026", "cards": [card(c) for c in sample], "total": len(Y),
         "totalLabel": "đã đọc", "unit": "công ty", "cols": 4, "cardH": 210, "credit": "Danh bạ công khai của Y Combinator, 4 đợt W26, P26, S26, F26. Logo thuộc các công ty."},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · ĐỌC MỘT STARTUP", "title": "Có thay việc của người không?", "cookbook": "Parallel questions",
         "idea": "Bốn câu trong một lần gọi, từ mô tả công khai của startup.", "stateLines": [f"{demo['name']} ({demo['batch']})", f"\"{demo['oneLiner']}\""],
         "questions": [{"name": "ai_core", "kind": "Noul", "text": "Lõi sản phẩm là AI?"}, {"name": "area", "kind": "Choice", "text": "Mảng nào?"},
                       {"name": "automates", "kind": "Noul", "text": "Tự động hóa việc người đang làm?"}, {"name": "job", "kind": "Choice", "text": "Thay nghề nào?"}],
         "results": [{"name": "ai_core", "value": f"có: {round(da['ai_core']['noul'] * 100)}%", "tone": "good"}, {"name": "area", "value": AREA_VI[da["area"]["choice"]]},
                     {"name": "automates", "value": f"có: {round(da['automates']['noul'] * 100)}%", "tone": "warn"}, {"name": "job", "value": JOB_VI[da["job"]["choice"]], "tone": "bad"}]},
        {"type": "bars", "key": "areas", "step": "BƯỚC 3 · MẢNG", "title": "Startup 2026 làm gì?",
         "bars": [{"label": AREA_VI[k], "value": v, "text": f"{v}", "tone": "good" if i == 0 else "jev"} for i, (k, v) in enumerate(area.most_common(7))],
         "note": f"{round(ai * 100)}% lấy AI làm lõi sản phẩm. {round(sf * 100)}% đặt ở San Francisco; đội trung vị {team:.0f} người."},
        {"type": "bars", "key": "jobs", "step": "BƯỚC 4 · NGHỀ BỊ NHẮM TỚI", "title": "Startup đang tự động hóa việc gì?",
         "bars": [{"label": JOB_VI[k], "value": v, "text": f"{v} công ty", "tone": "warn" if i < 3 else "jev"} for i, (k, v) in enumerate(jobs.most_common(8))],
         "note": f"{len(auto)} trên {len(Y)} startup ({round(100 * len(auto) / len(Y))}%) nhắm tới việc con người đang được trả lương để làm."},
        {"type": "bars", "key": "closed", "step": "BƯỚC 5 · CÔNG TY ĐÓNG CỬA", "title": "Ngành nào đóng cửa nhiều nhất",
         "bars": [{"label": SECTOR_VI[k], "value": v, "text": f"{v} tin", "tone": "bad" if i == 0 else "jev"} for i, (k, v) in enumerate(sector.most_common(6))],
         "note": f"{len(C):,} tiêu đề về một công ty cụ thể phá sản hoặc đóng cửa. Bị nhắc nhiều: {', '.join(c for c, _ in comp.most_common(4))}.".replace(",", ".", 1)},
        {"type": "bars", "key": "why", "step": "BƯỚC 6 · VÌ SAO ĐÓNG CỬA", "title": "Lý do được nêu",
         "bars": [{"label": REASON_VI[k], "value": v, "text": f"{round(100 * v / sum(stated.values()))}%", "tone": "bad" if i == 0 else "jev"} for i, (k, v) in enumerate(sorted(stated.items(), key=lambda kv: -kv[1])[:6])],
         "note": f"Trên {sum(stated.values())} tin có nêu lý do; {reason['not_stated']} tin không nêu."},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": "Đóng: bán lẻ, hàng không. Mở: AI agent",
         "tagline": f"{round(100 * len(auto) / len(Y))}% startup mới nhắm tự động hóa việc con người đang làm, nhiều nhất là phân tích dữ liệu và lập trình.",
         "stats": [{"value": str(len(Y)), "label": "startup YC 2026"}, {"value": f"{len(C):,}".replace(",", "."), "label": "tin đóng cửa"}, {"value": f"{spend['usd'] * 100:.0f} cent", "label": "tiền gọi Jev"}],
         "bullets": [f"{round(ai * 100)}% startup YC 2026 lấy AI làm lõi", f"Đóng cửa nhiều nhất: {SECTOR_VI[sector.most_common(1)[0][0]].lower()}", f"Lý do hay gặp nhất: {REASON_VI[max(stated, key=stated.get)].lower()}"],
         "footnote": "Startup YC là một vườn ươm, không đại diện mọi công ty mới. Tin đóng cửa là tiêu đề báo tiếng Anh, chủ yếu ở Mỹ; một công ty có thể có nhiều tin."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"yc": len(Y), "ai_core": round(ai, 3), "automates": len(auto), "area": area.most_common(), "jobs": jobs.most_common(), "sf": round(sf, 3), "team": team,
             "closures": len(C), "companies": comp.most_common(10), "sector": sector.most_common(), "reason": reason.most_common(), "cost": spend,
             "demo": {"name": demo["name"], "oneLiner": demo["oneLiner"], "job": da["job"]["choice"], "area": da["area"]["choice"]}}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False))


if __name__ == "__main__":
    main()
