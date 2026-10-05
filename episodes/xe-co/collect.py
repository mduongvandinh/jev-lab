"""Tải khiếu nại công khai của chủ xe Mỹ gửi NHTSA (cơ quan an toàn giao thông Mỹ, dữ liệu công) cho 10 dòng xe
cũng bán ở Việt Nam, đời 2021–2024. Mỗi dòng lấy tối đa PER_MODEL khiếu nại, rải đều các đời xe.

Ra: data/complaints.jsonl
"""
import json
import os
import random
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import get_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = [("toyota", "camry", "Toyota Camry"), ("toyota", "corolla cross", "Toyota Corolla Cross"), ("honda", "cr-v", "Honda CR-V"),
          ("honda", "civic", "Honda Civic"), ("mazda", "cx-5", "Mazda CX-5"), ("hyundai", "tucson", "Hyundai Tucson"),
          ("hyundai", "santa fe", "Hyundai Santa Fe"), ("kia", "seltos", "Kia Seltos"), ("kia", "sportage", "Kia Sportage"),
          ("mitsubishi", "outlander", "Mitsubishi Outlander")]
YEARS = (2021, 2022, 2023, 2024)
PER_MODEL = 120

if __name__ == "__main__":
    random.seed(11)
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    rows = []
    for make, model, name in MODELS:
        pool = []
        for y in YEARS:
            try:
                res = get_json("https://api.nhtsa.gov/complaints/complaintsByVehicle?" + urllib.parse.urlencode({"make": make, "model": model, "modelYear": y}), tries=2)
            except RuntimeError:
                continue
            pool += [{**r, "_year": y} for r in res.get("results", []) if len((r.get("summary") or "").split()) >= 15]
            time.sleep(1)
        pick = random.sample(pool, min(PER_MODEL, len(pool)))
        for r in pick:
            rows.append({"id": f"odi{r['odiNumber']}", "model": name, "year": r["_year"], "components": r.get("components"),
                         "crash": r.get("crash") in (True, "True"), "fire": r.get("fire") in (True, "True"),
                         "injuries": int(r.get("numberOfInjuries") or 0), "incident": r.get("dateOfIncident"), "summary": r["summary"].strip()})
        print("MODEL", name, "pool", len(pool), "pick", len(pick), flush=True)
    with open(os.path.join(HERE, "data", "complaints.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("COMPLAINTS", len(rows))
