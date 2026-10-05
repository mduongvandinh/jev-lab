"""Pre-parsed value extraction: regex tìm ứng viên, Jev chỉ CHỌN (Choice) — không tự gõ giá trị.

money(t): số tiền ($120k, $150,000, €80k, 120-150k USD...).  count(t): số người/việc bị cắt (1,200 / 10% / 300).
names(t): cụm Viết Hoa liên tiếp (ứng viên tên công ty).  months(t): "6 months", "a year"...
choice(name, instr, cands): tạo câu Choice có thêm lựa chọn "none"; trả None nếu không có ứng viên.
"""
import re

MONEY = re.compile(r"(?:[$€£]\s?\d[\d,.]*\s?[kKmM]?(?:\s?(?:-|–|to)\s?[$€£]?\s?\d[\d,.]*\s?[kKmM]?)?|\d[\d,.]*\s?[kK]\s?(?:USD|EUR|GBP|\$|€|£))")
COUNT = re.compile(r"\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?\s?%|\b\d{2,6}\b(?=\s+(?:\w+\s+)?(?:jobs|workers|employees|staff|staffers|people|positions|roles|layoffs|cuts))")
NAMES = re.compile(r"\b(?:[A-Z][\w&'.-]*|[A-Z]{2,})(?:\s+(?:[A-Z][\w&'.-]*|of|&))*")
MONTHS = re.compile(r"\b(?:\d+|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+(?:months?|years?|weeks?)\b", re.I)
STOP = {"The", "A", "An", "After", "As", "In", "On", "At", "Why", "How", "What", "New", "US", "U.S.", "UK", "AI", "CEO", "Report", "Exclusive", "Update", "More", "Over", "Nearly"}


def uniq(xs, n=25):
    return list(dict.fromkeys(x.strip(" ,.") for x in xs if x.strip(" ,.")))[:n]


def money(t):
    return uniq(m.group(0) for m in MONEY.finditer(t))


def count(t):
    return uniq(m.group(0) for m in COUNT.finditer(t))


def names(t):
    """Tiêu đề tin tiếng Anh viết hoa mọi chữ, nên lấy mọi cụm con 1–3 chữ của mỗi đoạn viết hoa làm ứng viên."""
    out = []
    for m in NAMES.finditer(t):
        words = m.group(0).split()
        for i in range(len(words)):
            for k in (1, 2, 3):
                span = " ".join(words[i:i + k])
                if i + k <= len(words) and span not in STOP and words[i] not in ("of", "&") and words[i + k - 1] not in ("of", "&"):
                    out.append(span)
    return uniq(out, 40)


def months(t):
    return uniq(m.group(0) for m in MONTHS.finditer(t))


def choice(instr, cands):
    if not cands:
        return None
    return {"type": "choice", "instructions": instr + " Choose none if no candidate fits.",
            "criteria": {**{f"c{i}": f'"{c}"' for i, c in enumerate(cands)}, "none": "None of these"}}
