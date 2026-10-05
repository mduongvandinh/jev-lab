"""Hàm dùng chung cho các tập Jev Lab: tải JSON công khai (có chờ lại), gọi Jev hàng loạt (chạy tiếp được), tính chi phí.

Giá Jev: $0.042 / 1 triệu token đầu vào, token đầu ra miễn phí (OpenRouter, typesafe/jev-1.13).
"""
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from jevcall import decide

MODEL = "typesafe/jev-1.13"
PRICE_PER_M_INPUT = 0.042
UA = {"User-Agent": "jev-lab/1.0 (https://github.com/mduongvandinh/jev-lab; research on public data)"}


def get_json(url, headers=None, tries=5):
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print("lỗi mạng:", str(e)[:120], flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Không tải được {url}")


def get_text(url, headers=None, tries=4):
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            print("lỗi mạng:", str(e)[:120], flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Không tải được {url}")


def read_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")] if os.path.exists(path) else []


def ask_all(rows, build, out_path, workers=6):
    """Mỗi dòng một request Jev (mọi câu hỏi gộp một lần gọi). Dòng đã có kết quả thì bỏ qua."""
    done = {r["id"] for r in read_jsonl(out_path) if "answers" in r}
    todo = [r for r in rows if r["id"] not in done]
    print("JEV todo", len(todo), "done", len(done), flush=True)

    def one(row):
        try:
            out = decide({"model": MODEL, **build(row)})
            return {"id": row["id"], "answers": out["response"]["answers"], "usage": out["response"].get("usage", {}),
                    "seconds": out.get("elapsed_seconds")}
        except Exception as e:
            return {"id": row["id"], "error": str(e)[:200]}

    with ThreadPoolExecutor(max_workers=workers) as pool, open(out_path, "a", encoding="utf-8") as f:
        for i, res in enumerate(pool.map(one, todo), 1):
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
            if i % 100 == 0:
                print("JEV", i, "/", len(todo), flush=True)
    results = [r for r in read_jsonl(out_path) if "answers" in r]
    print("JEV ok", len(results), "errors", sum(1 for r in read_jsonl(out_path) if "error" in r), flush=True)
    return {r["id"]: r for r in results}


def cost(results):
    tokens = sum((r.get("usage") or {}).get("input_tokens", 0) for r in results)
    return {"calls": len(results), "input_tokens": tokens, "usd": round(tokens / 1e6 * PRICE_PER_M_INPUT, 4)}


def top(probs):
    k = max(probs, key=probs.get)
    return k, probs[k]
