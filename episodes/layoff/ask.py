"""Tiêu đề tin layoff + chuyện kể sau layoff -> Jev.
Tin: có phải một công ty cụ thể cắt việc không, ngành, nước, lý do; tên công ty và số người bị cắt chỉ được CHỌN trong ứng viên regex.
Chuyện kể: sau đó làm gì, đổi sang nghề gì, cảm nhận hiện tại; thời gian tìm việc chọn trong ứng viên regex.
Ra: jev/news.jsonl, jev/stories.jsonl
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import ask_all, read_jsonl  # noqa: E402
from pick import choice, count, months, names  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SECTORS = {"software_internet": "Software, internet, SaaS, social media", "hardware_semis": "Hardware, semiconductors, electronics", "finance": "Banking, finance, insurance, fintech",
           "retail_ecommerce": "Retail, e-commerce, consumer goods", "media_entertainment": "Media, news, entertainment, games", "auto_manufacturing": "Automotive and manufacturing",
           "healthcare_pharma": "Healthcare, pharma, biotech", "government_public": "Government, public sector, education", "telecom": "Telecom", "energy": "Energy, oil, utilities",
           "logistics_travel": "Logistics, airlines, travel, hospitality", "consulting_services": "Consulting and professional services", "other": "Other or unclear"}
COUNTRIES = {"us": "United States", "uk": "United Kingdom", "germany": "Germany", "france": "France", "other_europe": "Other Europe", "india": "India", "china": "China",
             "japan_korea": "Japan or South Korea", "canada": "Canada", "australia": "Australia", "other": "Other or not stated"}
REASONS = {"ai_automation": "AI or automation", "cost_cutting": "Cost cutting, efficiency", "restructuring": "Restructuring or strategy shift", "weak_demand": "Weak demand or falling sales",
           "tariffs_trade": "Tariffs or trade", "closure_bankruptcy": "Closure, bankruptcy", "merger": "Merger or acquisition", "funding_cuts": "Government or funding cuts", "not_stated": "Not stated"}
OUTCOMES = {"same_field_job": "Found a new job in the same field", "different_field_job": "Found a job in a different field or role", "freelance": "Freelancing or contracting",
            "own_business": "Started their own business or startup", "still_searching": "Still searching", "break_retired": "Took a break, retired or left the workforce",
            "study": "Went back to school or retrained", "unclear": "Not stated"}
NEW_FIELD = {"software": "Still software engineering", "management": "Management", "data_ai": "Data or AI", "teaching": "Teaching or education", "trades": "Skilled trades or manual work",
             "healthcare": "Healthcare", "government": "Government or public sector", "sales_marketing": "Sales, marketing or customer roles", "other": "Something else", "none": "No change or not stated"}


def noul(q, t, f):
    return {"type": "noul", "instructions": q, "criteria": {"true": t, "false": f}}


def build_news(n):
    q = {"is_layoff": noul("Does this headline report a specific employer cutting jobs?", "A specific employer is cutting jobs", "No (general economy, opinion, or no job cuts)"),
         "sector": {"type": "choice", "instructions": "Which sector is the employer in?", "criteria": SECTORS},
         "country": {"type": "choice", "instructions": "In which country are the job cuts mainly?", "criteria": COUNTRIES},
         "reason": {"type": "choice", "instructions": "What reason does the headline give for the cuts?", "criteria": REASONS}}
    for key, instr, cands in (("company", "Which quoted text is the name of the employer cutting jobs?", names(n["title"])),
                              ("count", "Which quoted text is the number or share of jobs being cut?", count(n["title"]))):
        c = choice(instr, cands)
        if c:
            q[key] = c
    return {"state": {"news_headline": n["title"], "outlet": n["source"]}, "questions": q}


def build_story(s):
    q = {"personal": noul("Does the commenter describe being laid off themselves?", "They were personally laid off", "No, they talk about others or in general"),
         "outcome": {"type": "choice", "instructions": "What did the commenter do after the layoff?", "criteria": OUTCOMES},
         "new_field": {"type": "choice", "instructions": "If they changed work, what field did they move into?", "criteria": NEW_FIELD},
         "mood": {"type": "score", "instructions": "How does the commenter feel about their situation now?", "criteria": ["Very bad", "Bad", "Mixed", "Good", "Very good"]}}
    c = choice("Which quoted text is how long it took them to find new work after the layoff?", months(s["text"]))
    if c:
        q["time_to_job"] = c
    return {"state": {"comment": s["text"][:2500]}, "questions": q}


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    ask_all(read_jsonl(os.path.join(HERE, "data", "news.jsonl")), build_news, os.path.join(HERE, "jev", "news.jsonl"), workers=4)
    ask_all(read_jsonl(os.path.join(HERE, "data", "stories.jsonl")), build_story, os.path.join(HERE, "jev", "stories.jsonl"), workers=4)
