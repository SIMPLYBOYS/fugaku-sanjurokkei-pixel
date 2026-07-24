#!/usr/bin/env python3
"""從 assets/*.jpg 抽一組 N 色富嶽色盤 → assets/palette.json。
北斎系列以普魯士藍為主,和東海道的土色盤不同,故重抽。
用法: python3 tools/extract-palette.py [N]   (預設 16)
"""
import json, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
N = int(sys.argv[1]) if len(sys.argv) > 1 else 16
THUMB = 200  # 每幅取樣寬度

imgs = sorted((ROOT / "assets").glob("*.jpg"))
if not imgs:
    sys.exit("no assets/*.jpg — 先跑 fetch-met.py")

# 拼成一張長圖再自適應量化 (median cut),讓各幅依面積貢獻色彩
tiles = []
for p in imgs:
    im = Image.open(p).convert("RGB")
    tiles.append(im.resize((THUMB, round(im.height * THUMB / im.width)), Image.Resampling.LANCZOS))
W = THUMB
H = sum(t.height for t in tiles)
montage = Image.new("RGB", (W, H))
y = 0
for t in tiles:
    montage.paste(t, (0, y)); y += t.height

q = montage.quantize(colors=N, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
pal = q.getpalette()[: N * 3]
colors = [(pal[i], pal[i + 1], pal[i + 2]) for i in range(0, N * 3, 3)]
counts = {idx: cnt for cnt, idx in q.getcolors(W * H)}  # index -> count
total = W * H
# 依出現面積排序 (深到淺不強制,單純由多到少)
order = sorted(range(N), key=lambda i: -counts.get(i, 0))
hexes = ["#%02x%02x%02x" % colors[i] for i in order]
share = [round(counts.get(i, 0) / total, 4) for i in order]

out = ROOT / "assets/palette.json"
json.dump({"colors": hexes, "share": share, "n": N,
           "source": [p.name for p in imgs], "method": "PIL median-cut over asset montage"},
          open(out, "w"), indent=2)
for h, s in zip(hexes, share):
    print(f"{h}  {s*100:5.1f}%")
print(f"-> {out.relative_to(ROOT)}  ({N} colors)")
