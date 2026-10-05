"""Đọc bảng HTML của Wikipedia (không cần thư viện ngoài): mỗi ô giữ chữ và các liên kết; trải rowspan/colspan thành lưới.

tables(html) -> [bảng], bảng = [hàng], hàng = [(chữ, [href...])]
"""
import html as H
from html.parser import HTMLParser


class _Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.stack, self.cell, self.skip = [], [], None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self.stack.append([])
        elif tag == "tr" and self.stack:
            self.stack[-1].append([])
        elif tag in ("td", "th") and self.stack and self.stack[-1]:
            self.cell = [[], [], int(a.get("colspan", 1) or 1), int(a.get("rowspan", 1) or 1)]
        elif tag == "a" and self.cell is not None and (a.get("href") or "").startswith("/wiki/"):
            self.cell[1].append(H.unescape(a["href"][6:]))
        elif tag in ("sup", "style") or "display:none" in (a.get("style") or ""):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "table" and self.stack:
            self.out.append(self.stack.pop())
        elif tag in ("td", "th") and self.cell is not None and self.stack and self.stack[-1]:
            text = " ".join("".join(self.cell[0]).split())
            self.stack[-1][-1].append((text, self.cell[1], self.cell[2], self.cell[3]))
            self.cell = None
        elif tag in ("sup", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, d):
        if self.cell is not None and not self.skip:
            self.cell[0].append(d)


def tables(html):
    p = _Tables()
    p.feed(html)
    out = []
    for t in p.out:
        rows, pending = [], {}
        for row in t:
            line, col, i = [], 0, 0
            while i < len(row) or col in pending:
                if col in pending:
                    cell, left = pending[col]
                    line.append(cell)
                    if left > 1:
                        pending[col] = (cell, left - 1)
                    else:
                        del pending[col]
                    col += 1
                    continue
                text, links, cs, rs = row[i]
                i += 1
                for _ in range(cs):
                    line.append((text, links))
                    if rs > 1:
                        pending[col] = ((text, links), rs - 1)
                    col += 1
            rows.append(line)
        out.append(rows)
    return out
