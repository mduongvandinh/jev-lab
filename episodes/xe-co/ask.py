"""Hai lượt hỏi Jev cho mỗi khiếu nại.

Lượt 1 (Parallel questions, 1 request): system (Choice cấp 1), severity (Score), moving (Noul), unfixed (Noul),
  và mileage (Choice trên các con số regex tìm được: cookbook Pre-parsed value extraction, Jev chỉ chọn, không tự gõ số).
Lượt 2 (Hierarchical classification): issue (Choice cấp 2 trong nhánh hệ thống đã chọn).
Ra: jev/pass1.jsonl, jev/pass2.jsonl
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import ask_all, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

TREE = {
    "powertrain": ("Engine, transmission or drivetrain: stalling, hesitation, loss of power, rough shifting", {
        "stall_shutoff": "Engine stalls or shuts off", "power_loss_hesitation": "Hesitation, surging or loss of power while driving",
        "shifting": "Transmission shifting problems (jerky, delayed, slipping)", "noise_vibration": "Abnormal engine/drivetrain noise or vibration",
        "oil_dilution": "Oil level rising, oil dilution with fuel, or oil consumption", "other": "Other powertrain problem"}),
    "brakes": ("Brakes: pedal, braking power, ABS, parking brake", {
        "soft_or_failure": "Brake pedal soft/sinks or brakes fail to stop the car", "noise_wear": "Brake noise, grinding or premature wear",
        "parking_brake": "Electronic parking brake or brake hold problem", "other": "Other brake problem"}),
    "steering": ("Steering system", {
        "assist_loss": "Steering becomes heavy or loses power assist", "pulling_wander": "Car pulls, wanders or steering feels loose",
        "noise_clunk": "Steering noise, clunk or vibration", "other": "Other steering problem"}),
    "driver_assist": ("Driver assistance: automatic emergency braking, collision warnings, lane keeping, adaptive cruise", {
        "phantom_braking": "Car brakes suddenly by itself with no real obstacle", "false_warnings": "False collision or sensor warnings without braking",
        "lane_keep": "Lane keeping or lane centering steers wrongly", "cruise": "Adaptive cruise control misbehaves", "other": "Other driver-assist problem"}),
    "electrical": ("Electrical system: battery, wiring, lights, warning lights", {
        "battery_drain": "Battery drains or car will not start", "lights": "Headlights, tail lights or other lights fail",
        "warning_errors": "Warning lights or error messages appear", "other": "Other electrical problem"}),
    "infotainment": ("Screen, phone connection, backup camera, software", {
        "screen_freeze": "Screen freezes, goes black or reboots", "camera": "Backup or surround camera fails",
        "phone_audio": "Phone connection, audio or navigation fails", "other": "Other infotainment/software problem"}),
    "airbags_belts": ("Airbags and seat belts", {
        "airbag_deploy": "Airbag did not deploy or deployed wrongly", "airbag_warning": "Airbag warning light or sensor fault",
        "seat_belt": "Seat belt fault", "other": "Other airbag/belt problem"}),
    "body": ("Body, structure and visibility: doors, windows, sunroof, windshield, seats, leaks", {
        "windshield": "Windshield cracks or chips without clear impact", "water_leak": "Water leaks into the cabin",
        "doors_windows": "Doors, locks, windows or sunroof fail", "seats": "Seat problem", "other": "Other body problem"}),
    "fuel_exhaust": ("Fuel system, fuel smell or leak, exhaust fumes", {
        "fuel_smell_leak": "Fuel smell or fuel leak", "fumes": "Exhaust or burning smell inside the cabin",
        "fuel_gauge_pump": "Fuel pump or fuel gauge problem", "other": "Other fuel/exhaust problem"}),
    "climate": ("Heating, air conditioning, ventilation, defrost", {
        "ac": "Air conditioning not cooling", "heat_defrost": "Heater or defroster fails", "smell": "Bad smell or mold from vents", "other": "Other climate problem"}),
    "wheels_suspension": ("Tires, wheels, suspension", {
        "tires": "Tire failure or abnormal wear", "suspension": "Suspension noise or failure", "wheels": "Wheel or bearing problem", "other": "Other wheel/suspension problem"}),
    "other": ("None of the above, or unclear", {"other": "Unclear or other"}),
}

MILE_RE = re.compile(r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?\s?[kK]|\d{2,6})\s*(?:miles|mile|mi\b|k\s*miles)", re.I)


def mileage_candidates(text):
    return list(dict.fromkeys(m.group(0).strip() for m in MILE_RE.finditer(text)))[:20]


def state(c):
    return {"vehicle": f"{c['year']} {c['model']}", "owner_complaint": c["summary"][:2500], "crash_reported": c["crash"], "fire_reported": c["fire"]}


def build1(c):
    q = {
        "system": {"type": "choice", "instructions": "Which vehicle system is the main subject of this owner complaint?", "criteria": {k: v[0] for k, v in TREE.items()}},
        "severity": {"type": "score", "instructions": "How dangerous is the described problem for the people in or around the vehicle?",
                     "criteria": ["No safety risk: annoyance only", "Minor risk", "Moderate risk", "Serious risk: could plausibly cause a crash or injury", "Severe: caused or nearly caused a crash, fire or injury"]},
        "moving": {"type": "noul", "instructions": "Did the problem happen while the vehicle was moving?", "criteria": {"true": "It happened while driving", "false": "It happened while parked, starting or not stated"}},
        "unfixed": {"type": "noul", "instructions": "Does the owner say the dealer could not fix it, or that it came back after repair?",
                    "criteria": {"true": "Repair failed, no fix available, or problem recurred", "false": "Not stated, or the problem was fixed"}},
    }
    cands = mileage_candidates(c["summary"])
    if cands:
        q["mileage"] = {"type": "choice", "instructions": "Which quoted text is the vehicle's odometer mileage when the problem happened? Choose none if no candidate is the odometer reading.",
                        "criteria": {**{f"m{i}": f'"{t}"' for i, t in enumerate(cands)}, "none": "None of these is the odometer mileage"}}
    return {"state": state(c), "questions": q}


def build2(c):
    sub = TREE[c["system"]][1]
    return {"state": {**state(c), "vehicle_system": TREE[c["system"]][0]},
            "questions": {"issue": {"type": "choice", "instructions": "Within this vehicle system, which specific problem best describes the complaint?", "criteria": sub}}}


if __name__ == "__main__":
    rows = read_jsonl(os.path.join(HERE, "data", "complaints.jsonl"))
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    p1 = ask_all(rows, build1, os.path.join(HERE, "jev", "pass1.jsonl"))
    rows2 = [{**c, "system": p1[c["id"]]["answers"]["system"]["choice"]} for c in rows if c["id"] in p1]
    ask_all([c for c in rows2 if c["system"] != "other"], build2, os.path.join(HERE, "jev", "pass2.jsonl"))
