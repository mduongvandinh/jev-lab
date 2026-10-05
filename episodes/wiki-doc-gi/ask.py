"""Người Việt đọc gì trên Wikipedia — hai lượt hỏi Jev cho 1.500 bài nhiều lượt xem nhất.

Lượt 1 (Parallel questions): topic (Choice cấp 1), why (Choice: vì sao bài được đọc), vietnam (Noul),
  adult (Noul) và crime (Noul) — hai "trạm chắn" kiểu cookbook Guardrails: bài vượt ngưỡng chỉ hiện ô khóa, không lộ tên.
Lượt 2 (Hierarchical classification): sub (Choice cấp 2 trong nhánh của lượt 1).
Ra: jev/pass1.jsonl, jev/pass2.jsonl
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lab"))
from common import ask_all, read_jsonl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = {
    "people": ("A person", {"politician": "Politician or official", "entertainer": "Actor, singer, TV personality, influencer", "athlete": "Athlete or coach",
                            "historical": "Historical figure (king, general, revolutionary)", "business": "Businessperson", "other": "Other person"}),
    "entertainment": ("Film, TV, music, games, comics or shows", {"korean": "Korean drama, film or K-pop", "chinese": "Chinese drama or film", "vietnamese_show": "Vietnamese TV show, film or music",
                                                                  "western": "Western film, series or music", "anime_games": "Anime, manga or video games", "other": "Other entertainment"}),
    "sports": ("Sports, teams, tournaments", {"football": "Football (soccer)", "multi_sport": "Multi-sport games (Olympics, Asian Games, SEA Games)", "other": "Other sports"}),
    "places": ("Countries, provinces, cities, geography", {"vietnam_place": "Place in Vietnam", "country": "A country", "foreign_place": "Foreign city or region", "other": "Other geography"}),
    "history_politics": ("History, wars, politics, government, institutions", {"vn_history": "Vietnamese history", "world_history": "World history and wars",
                                                                               "government": "Government, party, institutions, laws", "other": "Other"}),
    "society_culture": ("Holidays, religion, language, education, customs", {"holiday": "Holiday or festival", "religion_belief": "Religion, belief, zodiac",
                                                                             "education": "Education and exams", "other": "Other society topic"}),
    "science_tech": ("Science, technology, health, nature", {"tech_ai": "Technology, AI, internet companies", "health": "Health and medicine", "nature": "Nature, animals, space", "other": "Other science"}),
    "crime_disaster": ("Crimes, court cases, accidents, disasters", {"crime": "Crime or court case", "disaster": "Natural disaster or accident", "other": "Other"}),
    "adult": ("Sexual or adult content", {"adult": "Adult content"}),
    "other": ("Something else", {"other": "Other"}),
}
WHY = {"evergreen": "Steady interest: school topics, reference, always read", "news": "In the news that month", "death": "Death of the person",
       "tv_airing": "TV show, drama or film being released or aired", "sports_event": "A sports event happening", "holiday": "Holiday or anniversary that month",
       "scandal_crime": "Scandal, crime or court case", "unclear": "Unclear"}


def noul(q, t, f):
    return {"type": "noul", "instructions": q, "criteria": {"true": t, "false": f}}


def state(a):
    return {"wikipedia_title": a["title"], "short_description": a.get("description") or "", "intro": (a.get("extract") or "")[:1000],
            "months_in_vietnamese_wikipedia_top_1000_last_12_months": a["months"], "peak_month": a["peak_month"]}


def build1(a):
    return {"state": state(a), "questions": {
        "topic": {"type": "choice", "instructions": "What is this Wikipedia article mainly about?", "criteria": {k: v[0] for k, v in TREE.items()}},
        "why": {"type": "choice", "instructions": "Why were Vietnamese readers most likely reading this article in its peak month?", "criteria": WHY},
        "vietnam": noul("Is the article about Vietnam or a Vietnamese subject?", "Vietnamese subject", "Not Vietnamese"),
        "adult": noul("Is the article mainly about sexual content, pornography or adult entertainment?", "Mainly sexual or adult content", "Not adult content"),
        "crime": noul("Is the article mainly about a violent crime involving identifiable private individuals (victims or suspects who are not public figures)?",
                      "Violent crime involving private individuals", "No"),
    }}


def build2(a):
    sub = TREE[a["topic"]][1]
    return {"state": state(a), "questions": {"sub": {"type": "choice", "instructions": f"Within the topic '{TREE[a['topic']][0]}', which sub-topic fits best?", "criteria": sub}}}


if __name__ == "__main__":
    rows = read_jsonl(os.path.join(HERE, "data", "articles.jsonl"))
    os.makedirs(os.path.join(HERE, "jev"), exist_ok=True)
    p1 = ask_all(rows, build1, os.path.join(HERE, "jev", "pass1.jsonl"), workers=6)
    rows2 = [{**a, "topic": p1[a["id"]]["answers"]["topic"]["choice"]} for a in rows if a["id"] in p1]
    ask_all([a for a in rows2 if len(TREE[a["topic"]][1]) > 1], build2, os.path.join(HERE, "jev", "pass2.jsonl"), workers=6)
