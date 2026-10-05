"""Tin tuyển dụng / hồ sơ tìm việc trên HN -> một request mỗi bài (Parallel questions).
Lương: regex tìm số tiền, Jev chỉ chọn mức thấp và cao (Pre-parsed value extraction).
Ra: jev/answers.jsonl
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import ask_all, read_jsonl  # noqa: E402
from pick import choice, money  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROLES = {"backend": "Backend engineer", "frontend": "Frontend engineer", "fullstack": "Full-stack engineer", "mobile": "Mobile engineer",
         "ml_ai": "ML / AI engineer or researcher", "data": "Data engineer, analyst or scientist", "devops_infra": "DevOps, SRE, infrastructure, platform",
         "security": "Security engineer", "embedded_hardware": "Embedded, firmware or hardware engineer", "design_product": "Product manager or designer",
         "leadership": "Engineering manager, CTO, tech lead", "other": "Other or many different roles"}
REGIONS = {"us": "United States", "canada": "Canada", "uk": "United Kingdom", "europe": "Europe (EU and rest of Europe, not UK)", "latam": "Latin America",
           "india": "India", "asia_other": "Asia except India", "oceania": "Australia or New Zealand", "africa_me": "Africa or Middle East", "anywhere": "Worldwide / anywhere remote", "unclear": "Not stated"}
REMOTE = {"remote": "Fully remote", "hybrid": "Hybrid", "onsite": "On-site only", "unclear": "Not stated"}
LEVEL = {"junior": "Junior / entry level", "mid": "Mid level", "senior": "Senior", "staff_plus": "Staff, principal or leadership", "unclear": "Not stated or mixed"}


def noul(q, t, f):
    return {"type": "noul", "instructions": q, "criteria": {"true": t, "false": f}}


def build(p):
    if p["kind"] == "hiring":
        q = {"role": {"type": "choice", "instructions": "Which role does this job post mainly hire for?", "criteria": ROLES},
             "region": {"type": "choice", "instructions": "Where is the job located (or where must candidates be)?", "criteria": REGIONS},
             "remote": {"type": "choice", "instructions": "What is the work arrangement?", "criteria": REMOTE},
             "level": {"type": "choice", "instructions": "What seniority does the post ask for?", "criteria": LEVEL},
             "ai_product": noul("Is the company's product built around AI, LLMs or agents?", "AI is core to the product", "AI is not core to the product"),
             "ai_skill": noul("Does the post ask candidates for experience with AI, LLMs or ML?", "AI/LLM/ML experience is requested", "Not requested"),
             "visa": noul("Does the post say it sponsors visas?", "Visa sponsorship offered", "Not offered or not stated")}
        c = money(p["text"])
        if c:
            q["salary_low"] = choice("Which quoted text is the LOWEST yearly base salary offered?", c)
            q["salary_high"] = choice("Which quoted text is the HIGHEST yearly base salary offered?", c)
        state = {"job_post": p["text"][:2500]}
    else:
        q = {"role": {"type": "choice", "instructions": "Which role is this job seeker mainly looking for?", "criteria": ROLES},
             "region": {"type": "choice", "instructions": "Where is the job seeker located?", "criteria": REGIONS},
             "remote": {"type": "choice", "instructions": "What work arrangement does the seeker want?", "criteria": REMOTE},
             "level": {"type": "choice", "instructions": "What seniority does the seeker appear to have?", "criteria": LEVEL},
             "ai_skill": noul("Does the seeker list experience with AI, LLMs or ML?", "Lists AI/LLM/ML experience", "Does not"),
             "laid_off": noul("Does the seeker mention being laid off or their company shutting down?", "Mentions a layoff or shutdown", "Does not")}
        state = {"job_seeker_post": p["text"][:2500]}
    return {"state": state, "questions": q}


if __name__ == "__main__":
    rows = read_jsonl(os.path.join(HERE, "data", "posts.jsonl"))
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    ask_all(rows, build, os.path.join(HERE, "jev", "answers.jsonl"), workers=4)
