"""Tải thời tiết từng ngày năm 2025 của 10 thành phố Việt Nam từ Open-Meteo (dữ liệu tái phân tích, CC BY 4.0).

Ra: data/days.jsonl, mỗi dòng một ngày của một thành phố.
"""
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CITIES = {
    "Hà Nội": (21.03, 105.85), "Hải Phòng": (20.86, 106.68), "Sa Pa": (22.34, 103.84), "Huế": (16.46, 107.59),
    "Đà Nẵng": (16.05, 108.20), "Nha Trang": (12.24, 109.19), "Đà Lạt": (11.94, 108.44), "TP.HCM": (10.78, 106.70),
    "Cần Thơ": (10.03, 105.78), "Phú Quốc": (10.22, 103.96),
}
DAILY = ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min",
         "precipitation_sum", "precipitation_hours", "wind_speed_10m_max", "relative_humidity_2m_mean", "sunshine_duration", "cloud_cover_mean"]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    rows = []
    for city, (lat, lon) in CITIES.items():
        q = {"latitude": lat, "longitude": lon, "start_date": "2025-01-01", "end_date": "2025-12-31", "daily": ",".join(DAILY), "timezone": "Asia/Bangkok"}
        d = get_json("https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(q))["daily"]
        for i, day in enumerate(d["time"]):
            rows.append({"id": f"{city}|{day}", "city": city, "date": day, **{k: d[k][i] for k in DAILY}})
        print("CITY", city, len(d["time"]), flush=True)
        time.sleep(2)
    with open(os.path.join(HERE, "data", "days.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("DAYS", len(rows))
