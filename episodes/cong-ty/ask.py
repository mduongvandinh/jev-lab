"""Công ty YC 2026 + tin đóng cửa 2026 -> Jev.
YC: lõi AI không, mảng, có tự động hóa việc con người đang làm không, thay nghề nào.
Đóng cửa: có phải một công ty cụ thể phá sản/đóng cửa không, ngành, nước, lý do; tên công ty CHỌN trong ứng viên regex.
Ra: jev/yc.jsonl, jev/closures.jsonl
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import ask_all, read_jsonl  # noqa: E402
from pick import choice, names  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "layoff"))
from ask import COUNTRIES, SECTORS, noul  # noqa: E402

AREAS = {"ai_agents_automation": "AI agents and workflow automation for businesses", "devtools": "Developer tools and infrastructure", "health": "Healthcare and biotech",
         "fintech": "Finance, insurance, accounting", "defense_hardware": "Defense, aerospace, hardware", "robotics": "Robotics and physical automation",
         "consumer": "Consumer apps", "vertical_saas": "Software for a specific industry (legal, construction, logistics...)", "climate_energy": "Climate and energy",
         "security": "Cybersecurity", "education": "Education", "other": "Other"}
JOBS = {"customer_support": "Customer support", "sales": "Sales and lead generation", "software_engineering": "Software engineering and QA", "legal": "Legal work",
        "accounting_finance": "Accounting, bookkeeping, finance ops", "recruiting_hr": "Recruiting and HR", "healthcare_admin": "Healthcare admin, medical scribing, billing",
        "data_analysis": "Data analysis and research", "manual_labor": "Physical or manual labor", "other": "Another job", "none": "Does not replace a human job"}
CLOSE_REASONS = {"debt_cash": "Debt or ran out of money", "weak_demand": "Weak demand or falling sales", "competition": "Lost to competition", "fraud_legal": "Fraud, lawsuits or legal trouble",
                 "tariffs_costs": "Tariffs or rising costs", "funding": "Could not raise funding", "acquired": "Acquired or merged", "regulation": "Regulation", "not_stated": "Not stated"}


def build_yc(c):
    return {"state": {"startup": c["name"], "one_liner": c["oneLiner"], "description": c["description"], "tags": c["tags"]},
            "questions": {"ai_core": noul("Is the product built around AI, LLMs or agents?", "AI is core", "AI is not core"),
                          "area": {"type": "choice", "instructions": "Which area is this startup in?", "criteria": AREAS},
                          "automates": noul("Does the product aim to automate work that people are currently paid to do?", "Automates human work", "Does not"),
                          "job": {"type": "choice", "instructions": "Which human job does the product mainly automate?", "criteria": JOBS}}}


def build_close(n):
    q = {"is_closure": noul("Does this headline report a specific company going bankrupt, closing, or shutting down?", "A specific company is bankrupt or closing", "No"),
         "sector": {"type": "choice", "instructions": "Which sector is the company in?", "criteria": SECTORS},
         "country": {"type": "choice", "instructions": "In which country is the company mainly?", "criteria": COUNTRIES},
         "reason": {"type": "choice", "instructions": "What reason does the headline give?", "criteria": CLOSE_REASONS}}
    c = choice("Which quoted text is the name of the company that is closing or bankrupt?", names(n["title"]))
    if c:
        q["company"] = c
    return {"state": {"news_headline": n["title"], "outlet": n["source"]}, "questions": q}


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    ask_all(read_jsonl(os.path.join(HERE, "data", "yc.jsonl")), build_yc, os.path.join(HERE, "jev", "yc.jsonl"), workers=4)
    ask_all(read_jsonl(os.path.join(HERE, "data", "closures.jsonl")), build_close, os.path.join(HERE, "jev", "closures.jsonl"), workers=4)
