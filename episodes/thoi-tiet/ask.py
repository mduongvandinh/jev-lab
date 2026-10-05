"""Mỗi ngày một request Jev, gộp 4 câu (cookbook Parallel questions):
comfort (Score 0–4), kind (Choice), laundry (Noul), umbrella (Noul).
Thêm một thử nghiệm Self-consistency: hỏi lại 3 ngày 15 lần, đo độ lệch.
Ra: jev/answers.jsonl, jev/consistency.json
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import MODEL, ask_all, read_jsonl  # noqa: E402
from jevcall import decide  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

KINDS = {
    "hot_sunny": "Hot and sunny; feels like 35°C or more at midday",
    "warm_pleasant": "Warm, mostly dry, comfortable",
    "cool_pleasant": "Cool, dry and fresh",
    "cold": "Cold; feels below about 15°C for much of the day",
    "muggy": "Muggy and damp: very humid, sticky, little sun, little or no rain",
    "drizzle_gray": "Gray and overcast with light drizzle",
    "rainy": "Rainy: steady or repeated rain",
    "heavy_rain_storm": "Heavy rain or storm conditions",
}

QUESTIONS = {
    "comfort": {"type": "score", "instructions": "How pleasant is this day for spending time outdoors (walking, sightseeing, a picnic) for a typical local person?",
                "criteria": ["Miserable: better to stay inside", "Unpleasant", "Okay", "Pleasant", "Ideal day to be outside"]},
    "kind": {"type": "choice", "instructions": "Which description fits this day's weather best?", "criteria": KINDS},
    "laundry": {"type": "noul", "instructions": "Would laundry hung outdoors dry well during this day?",
                "criteria": {"true": "Laundry would dry well outdoors", "false": "Laundry would stay damp or get wet"}},
    "umbrella": {"type": "noul", "instructions": "Should a person carry an umbrella or raincoat when going out on this day?",
                 "criteria": {"true": "Yes, rain is likely enough to need one", "false": "No, rain gear is unnecessary"}},
}


def state(d):
    return {
        "place": f"{d['city']}, Vietnam", "date": d["date"],
        "temperature_max_c": d["temperature_2m_max"], "temperature_min_c": d["temperature_2m_min"],
        "feels_like_max_c": d["apparent_temperature_max"], "feels_like_min_c": d["apparent_temperature_min"],
        "rain_total_mm": d["precipitation_sum"], "hours_with_rain": d["precipitation_hours"],
        "max_wind_kmh": d["wind_speed_10m_max"], "mean_humidity_pct": d["relative_humidity_2m_mean"],
        "sunshine_hours": round((d["sunshine_duration"] or 0) / 3600, 1), "mean_cloud_cover_pct": d["cloud_cover_mean"],
    }


def build(d):
    return {"state": state(d), "questions": QUESTIONS}


def consistency(days, n=15):
    """Self-consistency: hỏi lại cùng một ngày n lần, đo độ lệch chuẩn của điểm dễ chịu và của Noul áo mưa."""
    out = []
    for d in days:
        runs = [decide({"model": MODEL, **build(d)})["response"]["answers"] for _ in range(n)]
        comfort = [r["comfort"]["score"] for r in runs]
        umb = [r["umbrella"]["noul"] for r in runs]
        kinds = [r["kind"]["choice"] for r in runs]
        out.append({"id": d["id"], "comfort": comfort, "umbrella": umb, "kinds": kinds,
                    "comfort_mean": round(statistics.mean(comfort), 3), "comfort_sd": round(statistics.pstdev(comfort), 4),
                    "umbrella_mean": round(statistics.mean(umb), 3), "umbrella_sd": round(statistics.pstdev(umb), 4),
                    "kind_same": max(kinds.count(k) for k in set(kinds)), "runs": n})
        print("CONSIST", out[-1], flush=True)
    return out


if __name__ == "__main__":
    days = read_jsonl(os.path.join(HERE, "data", "days.jsonl"))
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    if "--only-consistency" not in sys.argv:
        ask_all(days, build, os.path.join(HERE, "jev", "answers.jsonl"))
    if "--consistency" in sys.argv or "--only-consistency" in sys.argv:
        by = {d["id"]: d for d in days}
        picks = [by[i] for i in ("Hà Nội|2025-03-12", "Đà Lạt|2025-07-20", "TP.HCM|2025-04-15")]
        json.dump(consistency(picks), open(os.path.join(HERE, "jev", "consistency.json"), "w"), ensure_ascii=False, indent=1)
