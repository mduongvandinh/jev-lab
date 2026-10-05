"""Ghép ảnh thu nhỏ thành tấm 4x4 có đánh số để agent mô tả 16 tác phẩm mỗi lần xem.

Cần Pillow: pip install pillow && python3 make_sheets.py
Ra: sheets/sheet_NNN.png và sheets/index.json {sheet: [id1..id16]}. Chỉ tạo tấm mới cho ảnh chưa ghép.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
CELL, COLS, PER = 320, 4, 16
OUT = os.path.join(ROOT, "sheets")


def main():
    os.makedirs(OUT, exist_ok=True)
    kept = [json.loads(l) for l in open(os.path.join(ROOT, "data", "kept.jsonl"), encoding="utf-8")]
    index_path = os.path.join(OUT, "index.json")
    index = json.load(open(index_path)) if os.path.exists(index_path) else {}
    done = {i for ids in index.values() for i in ids}
    todo = [k["id"] for k in kept if k["id"] not in done]
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 34)
    n = len(index)
    for start in range(0, len(todo) - len(todo) % PER, PER):  # chỉ ghép tấm đủ 16 ảnh
        ids = todo[start:start + PER]
        sheet = Image.new("RGB", (CELL * COLS, CELL * (PER // COLS)), "white")
        draw = ImageDraw.Draw(sheet)
        for i, rid in enumerate(ids):
            img = Image.open(os.path.join(ROOT, "thumbs", f"{rid}.jpg")).convert("RGB")
            img.thumbnail((CELL - 12, CELL - 12))
            x, y = (i % COLS) * CELL, (i // COLS) * CELL
            sheet.paste(img, (x + (CELL - img.width) // 2, y + (CELL - img.height) // 2))
            draw.rectangle([x + 4, y + 4, x + 58, y + 46], fill="black")
            draw.text((x + 10, y + 6), str(i + 1), fill="yellow", font=font)
        name = f"sheet_{n:03d}"
        sheet.save(os.path.join(OUT, f"{name}.png"), optimize=True)
        index[name] = ids
        n += 1
    json.dump(index, open(index_path, "w"), indent=1)
    print("SHEETS", len(index), "covering", sum(len(v) for v in index.values()), "works")


if __name__ == "__main__":
    main()
