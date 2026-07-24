#!/usr/bin/env python3
"""把每幅的細節框畫在場景上,拼成 QA 檢視圖(供人工核對框位是否對)。
用法: python3 tools/qa-hits.py [n1 n2 ...]   不給參數=全部有 hits 的
輸出到 $TMPDIR/qa-hits-*.jpg (每 12 幅一張)。
"""
import os, sys, json, math
from pathlib import Path
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("TMPDIR", "/tmp"))
prints = json.load(open(ROOT / "data/prints.json", encoding="utf-8"))["prints"]
want = set(int(x) for x in sys.argv[1:])
sel = [p for p in prints if p.get("hits") and (not want or p["n"] in want)]

TW = 360                      # tile scene width
PER = 12                      # tiles per montage
COLORS = [(255, 90, 60), (90, 200, 120), (110, 170, 255)]

def tile(p):
    im = Image.open(ROOT / f"game-assets/scenes/{p['slug']}.png").convert("RGB")
    th = round(im.height * TW / im.width)
    im = im.resize((TW, th))
    d = ImageDraw.Draw(im)
    for i, hb in enumerate(p["hits"]):
        x, y, w, h = hb["rect"]
        d.rectangle([x*TW, y*th, (x+w)*TW, (y+h)*th], outline=COLORS[i % 3], width=3)
        d.text((x*TW+2, y*th+2), str(i+1), fill=COLORS[i % 3])
    d.text((3, 3), f"{p['n']:02d} {p['slug']}", fill=(255, 255, 0))
    return im

for b in range(0, len(sel), PER):
    batch = sel[b:b+PER]
    cols = 3
    rows = math.ceil(len(batch)/cols)
    tiles = [tile(p) for p in batch]
    tw = TW; th = max(t.height for t in tiles); pad = 8
    m = Image.new("RGB", (cols*tw+(cols+1)*pad, rows*th+(rows+1)*pad), (30, 30, 36))
    for i, t in enumerate(tiles):
        cx = pad+(i % cols)*(tw+pad); cy = pad+(i//cols)*(th+pad)
        m.paste(t, (cx, cy))
    out = OUT / f"qa-hits-{b//PER+1}.jpg"
    m.save(out, quality=88)
    print(f"{out}  ({len(batch)} prints)")
