#!/bin/bash
# Render một khung ở ~70% mỗi cảnh của tập <slug>, ghép thành stills/<slug>-sheet.png để soát bố cục
set -e
SLUG=$1; ROOT="$(cd "$(dirname "$0")/.." && pwd)"; OUT="$ROOT/stills"; mkdir -p "$OUT"
FRAMES=$(python3 - "$ROOT" "$SLUG" <<'PY'
import json, math, sys
root, slug = sys.argv[1], sys.argv[2]
e = json.load(open(f"{root}/viz/src/data/episodes.json"))[slug]
base = {"intro": 90, "scan": 300, "technique": 360, "label": 390, "heat": 330, "bars": 300, "repeat": 300, "judge": 400, "reveal": 420, "pitch": 330, "timeline": 420, "columns": 360}
f, out = 0, []
for s in e["episode"]["scenes"]:
    n = max(base[s["type"]], 8 + math.ceil(e["voice"].get(s["key"], {}).get("seconds", 0) * 30) + 30)
    out.append(str(f + int(n * 0.7)))
    f += n
print(" ".join(out))
PY
)
cd "$ROOT/viz"
ARGS=()
for fr in $FRAMES; do
  npx remotion still src/index.ts "Lab-$SLUG" "$OUT/$SLUG-$fr.png" --frame="$fr" --log=error
  ARGS+=(-i "$OUT/$SLUG-$fr.png")
done
N=$(echo $FRAMES | wc -w | tr -d ' ')
ffmpeg -v error -y "${ARGS[@]}" -filter_complex "hstack=inputs=$N,scale=$((N * 300)):-1" "$OUT/$SLUG-sheet.png"
echo "SHEET $OUT/$SLUG-sheet.png"
