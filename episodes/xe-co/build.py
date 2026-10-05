"""Biến khiếu nại NHTSA + đáp án Jev thành episode.json cho tập "xe cộ".

- Hierarchical classification: hệ thống (cấp 1) -> lỗi cụ thể (cấp 2); cấp 2 có confidence < 0,6 thì chỉ báo cấp 1.
- Pre-parsed value extraction: số dặm do regex tìm, Jev chỉ chọn; đổi sang km.
- Hai ngưỡng kiểu cookbook Guardrails: ưu tiên / xem xét / theo dõi.
- Kiểm tra chéo: nhãn hệ thống của Jev có khớp nhãn bộ phận NHTSA gắn sẵn không.
"""
import json
import os
import random
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import cost, read_jsonl  # noqa: E402
from ask import mileage_candidates  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CONF = 0.6
SYS_VI = {"powertrain": "Động cơ, hộp số", "brakes": "Phanh", "steering": "Tay lái", "driver_assist": "Hỗ trợ lái", "electrical": "Điện",
          "infotainment": "Màn hình, camera", "airbags_belts": "Túi khí, dây đai", "body": "Thân, cửa, kính", "fuel_exhaust": "Nhiên liệu, khí thải",
          "climate": "Điều hòa", "wheels_suspension": "Lốp, treo", "other": "Khác"}
ISSUE_VI = {"stall_shutoff": "Chết máy", "power_loss_hesitation": "Hụt ga, ì máy", "shifting": "Sang số giật", "noise_vibration": "Tiếng ồn, rung",
            "oil_dilution": "Dầu máy lẫn xăng", "soft_or_failure": "Phanh mất lực", "noise_wear": "Phanh kêu, mòn nhanh", "parking_brake": "Phanh tay điện",
            "assist_loss": "Mất trợ lực lái", "pulling_wander": "Lái bị lệch, lỏng", "noise_clunk": "Lái kêu lục cục", "phantom_braking": "Tự phanh vô cớ",
            "false_warnings": "Cảnh báo sai", "lane_keep": "Giữ làn đánh lái sai", "cruise": "Ga tự động lỗi", "battery_drain": "Hết ắc quy",
            "lights": "Đèn hỏng", "warning_errors": "Báo lỗi trên đồng hồ", "screen_freeze": "Màn hình treo", "camera": "Camera lùi hỏng",
            "phone_audio": "Kết nối điện thoại", "airbag_deploy": "Túi khí không bung", "airbag_warning": "Đèn báo túi khí", "seat_belt": "Dây đai lỗi",
            "windshield": "Kính lái tự nứt", "water_leak": "Thấm nước", "doors_windows": "Cửa, kính, cửa sổ trời", "seats": "Ghế",
            "fuel_smell_leak": "Mùi xăng, rò xăng", "fumes": "Mùi khét trong xe", "fuel_gauge_pump": "Bơm xăng, đồng hồ xăng", "ac": "Điều hòa không mát",
            "heat_defrost": "Sưởi, sấy kính", "smell": "Mùi hôi cửa gió", "tires": "Lốp hỏng", "suspension": "Hệ treo", "wheels": "Bánh, bi moay-ơ", "other": "Lỗi khác"}
NHTSA_MAP = {"powertrain": ["ENGINE", "POWER TRAIN", "PROPULSION", "SPEED CONTROL"], "brakes": ["BRAKE"], "steering": ["STEERING"],
             "driver_assist": ["FORWARD COLLISION", "LANE DEPARTURE", "SPEED CONTROL", "BACK OVER"], "electrical": ["ELECTRICAL", "LIGHTING"],
             "infotainment": ["BACK OVER", "ELECTRICAL", "VISIBILITY"], "airbags_belts": ["AIR BAG", "SEAT BELT"],
             "body": ["STRUCTURE", "VISIBILITY", "LATCHES", "SEATS", "EQUIPMENT"], "fuel_exhaust": ["FUEL", "ENGINE"], "climate": ["EQUIPMENT", "VISIBILITY", "ELECTRICAL"],
             "wheels_suspension": ["TIRE", "WHEEL", "SUSPENSION"], "other": []}


def triage(r):
    if r["severity"] >= 3 and r["moving"] >= 0.7:
        return "ƯU TIÊN", "bad"
    if r["severity"] >= 2 or r["unfixed"] >= 0.7:
        return "XEM XÉT", "warn"
    return "THEO DÕI", "good"


def snippet(t, n=90):
    t = " ".join(t.split())
    return "“" + (t[:n].rsplit(" ", 1)[0] + "…" if len(t) > n else t) + "”"


def main():
    rows = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "data", "complaints.jsonl"))}
    p1 = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "pass1.jsonl")) if "answers" in r}
    p2 = {r["id"]: r for r in read_jsonl(os.path.join(HERE, "jev", "pass2.jsonl")) if "answers" in r}
    data = []
    for i, r in p1.items():
        a, c = r["answers"], rows[i]
        sysk = a["system"]["choice"]
        iss = p2.get(i, {}).get("answers", {}).get("issue")
        miles = None
        if "mileage" in a and a["mileage"]["choice"] != "none":
            txt = mileage_candidates(c["summary"])[int(a["mileage"]["choice"][1:])]
            num = txt.lower().split("mi")[0].replace(",", "").strip()
            miles = float(num[:-1]) * 1000 if num.endswith("k") else float(num) if num.replace(".", "").isdigit() else None
        data.append({**c, "system": sysk, "sys_conf": a["system"]["confidence"], "issue": iss["choice"] if iss else None,
                     "issue_conf": iss["confidence"] if iss else 0, "severity": a["severity"]["score"], "moving": a["moving"]["noul"],
                     "unfixed": a["unfixed"]["noul"], "miles": miles, "mileage_pick": a.get("mileage", {}).get("choice")})
    n = len(data)
    models = list(dict.fromkeys(c["model"] for c in rows.values()))
    systems = [s for s, _ in Counter(d["system"] for d in data).most_common() if s != "other"][:7]
    by_model = defaultdict(list)
    for d in data:
        by_model[d["model"]].append(d)
    share = [[round(100 * sum(d["system"] == s for d in by_model[m]) / len(by_model[m])) for s in systems] for m in models]
    sure_issue = [d for d in data if d["issue"] and d["issue"] != "other" and d["issue_conf"] >= CONF]
    issues = Counter(d["issue"] for d in sure_issue).most_common(8)
    top_issue = {m: Counter(d["issue"] for d in by_model[m] if d["issue"] and d["issue"] != "other" and d["issue_conf"] >= CONF).most_common(1)[0] for m in models}
    agree = [any(k in (d["components"] or "") for k in NHTSA_MAP[d["system"]]) for d in data if d["system"] != "other"]
    agree_pct = round(100 * sum(agree) / len(agree))
    moving_pct = round(100 * sum(d["moving"] >= 0.5 for d in data) / n)
    unsure_issue = sum(1 for d in data if d["issue"] and d["issue_conf"] < CONF)
    with_miles = [d for d in data if d["miles"] and 100 <= d["miles"] <= 300000]
    km_by_sys = {s: statistics.median(d["miles"] * 1.609 for d in with_miles if d["system"] == s) for s in systems if sum(d["system"] == s for d in with_miles) >= 8}
    tri = Counter(triage(d)[0] for d in data)
    spend = cost(list(p1.values()) + list(p2.values()))

    random.seed(5)
    sample = random.sample(data, 140)

    def card(d, sub=True):
        tags = [t for t, on in (("va chạm", d["crash"]), ("cháy", d["fire"])) if on]
        return {"icon": "🚗", "title": f"{d['model']} {d['year']}", "sub": snippet(d["summary"]) if sub else None, "lines": tags or None}

    demo = next(d for d in data if d["miles"] and d["system"] == "powertrain" and d["issue"] == "stall_shutoff" and d["moving"] > 0.8)
    demo_cands = mileage_candidates(demo["summary"])
    ex = []
    for want in ("stall_shutoff", "assist_loss", "phantom_braking", "windshield"):
        d = next(x for x in sorted(data, key=lambda x: x["id"]) if x["issue"] == want and x["issue_conf"] >= 0.8 and len(x["summary"]) < 900)
        ex.append(d)
    unsure_ex = next(x for x in sorted(data, key=lambda x: x["id"]) if x["issue"] and 0.3 < x["issue_conf"] < 0.5)

    def path(d):
        return f"{SYS_VI[d['system']]} › {ISSUE_VI[d['issue']]}" if d["issue_conf"] >= CONF else f"{SYS_VI[d['system']]} › (chưa chắc)"

    judge_pick = []
    for want in ("ƯU TIÊN", "THEO DÕI", "XEM XÉT", "ƯU TIÊN", "XEM XÉT"):
        judge_pick.append(next(d for d in sorted(data, key=lambda x: x["id"])[len(judge_pick) * 37:] if triage(d)[0] == want and len(d["summary"]) < 700))

    top_sys = systems[0]
    ep = {"slug": "xe-co", "title": "Chủ xe phàn nàn gì nhiều nhất?", "accent": "#f97316", "scenes": [
        {"type": "intro", "key": "intro", "kicker": "THÍ NGHIỆM VỚI JEV · XE CỘ", "headline": "Chủ xe phàn nàn gì nhiều nhất?",
         "sub": f"{n:,} khiếu nại thật về 10 dòng xe quen thuộc ở Việt Nam, AI đọc từng cái".replace(",", ".")},
        {"type": "scan", "key": "scan", "step": "BƯỚC 1 · DỮ LIỆU THẬT", "title": "Mỗi thẻ là một lời phàn nàn", "cards": [card(d) for d in sample],
         "total": n, "totalLabel": "đã đọc", "unit": "khiếu nại", "cols": 3, "cardH": 230,
         "credit": "Dữ liệu công khai của NHTSA (Mỹ), xe đời 2021–2024; khiếu nại do chủ xe tự gửi, chưa kiểm chứng"},
        {"type": "technique", "key": "technique", "step": "BƯỚC 2 · MỘT LẦN GỌI, NĂM CÂU", "title": "Đọc một lời phàn nàn", "cookbook": "Parallel questions · Pre-parsed value extraction",
         "idea": "Năm câu gộp một request. Số dặm thì Jev chỉ được chọn trong các số có sẵn trong bài, không tự gõ.",
         "stateLines": [f"{demo['year']} {demo['model']}", snippet(demo["summary"], 110), "Ứng viên số dặm: " + ", ".join(demo_cands[:3])],
         "questions": [{"name": "system", "kind": "Choice", "text": "Hệ thống nào bị lỗi?"}, {"name": "severity", "kind": "Score", "text": "Nguy hiểm đến mức nào?"},
                       {"name": "moving", "kind": "Noul", "text": "Xảy ra khi đang chạy?"}, {"name": "unfixed", "kind": "Noul", "text": "Sửa rồi vẫn bị?"},
                       {"name": "mileage", "kind": "Choice", "text": "Số dặm lúc gặp lỗi?"}],
         "results": [{"name": "system", "value": SYS_VI[demo["system"]]}, {"name": "severity", "value": f"{demo['severity']:.2f}/4".replace(".", ","), "tone": "bad"},
                     {"name": "moving", "value": f"có: {round(demo['moving'] * 100)}%", "tone": "warn"}, {"name": "unfixed", "value": f"có: {round(demo['unfixed'] * 100)}%", "tone": "muted"},
                     {"name": "mileage", "value": f"{demo_cands[int(demo['mileage_pick'][1:])]} ≈ {round(demo['miles'] * 1.609):,} km".replace(",", "."), "tone": "good"}]},
        {"type": "label", "key": "label", "step": "BƯỚC 3 · XẾP VÀO CÂY LỖI", "title": "Hệ thống trước, lỗi cụ thể sau", "cookbook": "Hierarchical classification",
         "examples": [{"card": card(d), "answers": [{"q": "Phân loại", "text": path(d), "prob": d["issue_conf"]},
                                                     {"q": "Nguy hiểm", "text": f"{d['severity']:.1f}/4".replace(".", ","), "tone": "bad" if d["severity"] >= 3 else "warn"},
                                                     {"q": "Đang chạy", "text": "có" if d["moving"] >= 0.5 else "không", "prob": d["moving"]}]} for d in ex[:3] + [unsure_ex]],
         "tally": {"title": "Hệ thống bị phàn nàn nhiều nhất", "bars": [{"label": SYS_VI[s], "value": sum(d["system"] == s for d in data)} for s in systems[:5]]}},
        {"type": "heat", "key": "heat", "step": "BƯỚC 4 · TỪNG DÒNG XE", "title": "Mỗi dòng xe hay bị gì?", "rows": [m.replace("Mitsubishi ", "Mitsu. ") for m in models],
         "cols": ["Máy", "Lái", "Thân", "Điện", "HTL", "Túi khí", "Phanh"][: len(systems)] if systems == ["powertrain", "steering", "body", "electrical", "driver_assist", "airbags_belts", "brakes"] else [SYS_VI[s][:6] for s in systems],
         "values": share, "highlight": [[i, max(range(len(systems)), key=lambda j: share[i][j])] for i in range(len(models))],
         "legend": "% khiếu nại của mỗi dòng xe rơi vào từng hệ thống (HTL: hỗ trợ lái). Ô viền vàng: nhiều nhất"},
        {"type": "bars", "key": "bars", "step": "BƯỚC 5 · LỖI CỤ THỂ", "title": "Top lỗi bị kể nhiều nhất",
         "bars": [{"label": ISSUE_VI[k], "value": v, "text": f"{v} lần", "tone": "bad" if i < 3 else "jev"} for i, (k, v) in enumerate(issues)],
         "note": f"Chỉ tính {len(sure_issue)} khiếu nại Jev chắc chắn về lỗi cụ thể (confidence từ 0,6)"},
        {"type": "judge", "key": "judge", "step": "BƯỚC 6 · PHÂN LOẠI MỨC ĐỘ", "title": "Cái nào cần xử lý trước?", "cookbook": "Ngưỡng hành động kiểu Guardrails",
         "items": [{"card": card(d), "pass": triage(d)[0] != "ƯU TIÊN", "stamp": triage(d)[0],
                    "metrics": [{"label": "Nguy hiểm", "value": d["severity"] / 4, "text": f"{d['severity']:.1f}/4".replace(".", ","), "tone": "bad"},
                                {"label": "Đang chạy", "value": d["moving"], "text": f"{round(d['moving'] * 100)}%", "tone": "warn"},
                                {"label": "Sửa vẫn bị", "value": d["unfixed"], "text": f"{round(d['unfixed'] * 100)}%", "tone": "muted"}]} for d in judge_pick]},
        {"type": "bars", "key": "km", "step": "BƯỚC 7 · LỖI XUẤT HIỆN KHI NÀO?", "title": "Đi bao nhiêu km thì gặp lỗi?", "cookbook": "Pre-parsed value extraction",
         "bars": [{"label": SYS_VI[s], "value": v, "text": f"{round(v / 1000)}k km", "tone": "jev"} for s, v in sorted(km_by_sys.items(), key=lambda kv: kv[1])],
         "note": f"Trung vị, từ {len(with_miles)} khiếu nại có ghi số dặm; Jev chọn đúng con số trong bài, không tự gõ"},
        {"type": "reveal", "key": "reveal", "kicker": "KẾT QUẢ", "headline": f"Nhiều nhất: {ISSUE_VI[issues[0][0]]}", "tagline": f"Tiếp theo là {ISSUE_VI[issues[1][0]].lower()} và {ISSUE_VI[issues[2][0]].lower()}. {moving_pct}% sự cố xảy ra khi xe đang chạy.",
         "stats": [{"value": f"{n:,}".replace(",", "."), "label": "khiếu nại đã đọc"}, {"value": f"{agree_pct}%", "label": "khớp nhãn bộ phận của NHTSA"},
                   {"value": f"{spend['usd']:.2f} USD".replace(".", ","), "label": "tiền gọi Jev"}],
         "bullets": [], "gridTitle": "Lỗi hay gặp nhất của từng dòng", "gridCols": 1, "grid": [{"label": m.replace("Mitsubishi ", "Mitsu. ").replace("Hyundai ", "Hyundai ").replace("Toyota Corolla Cross", "Corolla Cross"), "value": ISSUE_VI[top_issue[m][0]]} for m in models],
         "footnote": "Khiếu nại ở Mỹ, do chủ xe tự gửi, chưa kiểm chứng; dòng bán chạy thì nhiều khiếu nại hơn. Đây không phải bảng xếp hạng độ bền."},
    ]}
    json.dump(ep, open(os.path.join(HERE, "episode.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {"n": n, "systems": Counter(d["system"] for d in data).most_common(), "issues": issues, "top_issue": {m: v for m, v in top_issue.items()},
             "agree_pct": agree_pct, "moving_pct": moving_pct, "unsure_issue": unsure_issue, "km_by_sys": {k: round(v) for k, v in km_by_sys.items()},
             "with_miles": len(with_miles), "triage": tri, "cost": spend, "demo": {k: demo[k] for k in ("model", "year", "system", "issue", "severity", "moving", "unfixed", "miles")},
             "examples": [(d["model"], path(d), round(d["issue_conf"], 2)) for d in ex[:3] + [unsure_ex]], "judge": [(d["model"], triage(d)[0]) for d in judge_pick],
             "share": dict(zip(models, share)), "systems_cols": systems}
    json.dump(facts, open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False))


if __name__ == "__main__":
    main()
