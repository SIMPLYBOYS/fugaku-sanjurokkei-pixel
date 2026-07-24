#!/usr/bin/env python3
"""高解析框位核對:把每幅的 3 個細節框畫在 1000px 原圖上,放大拼圖(每張 4 幅)。
框旁標編號 1/2/3(對應 hits 順序);供人工逐幅核對框是否真的框住所描述的內容。
用法: python3 tools/qa-hires.py [n1 n2 ...]   不給=全部
輸出 $TMPDIR/hires-*.jpg
"""
import os, sys, json, math
from pathlib import Path
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("TMPDIR", "/tmp"))
prints = json.load(open(ROOT / "data/prints.json", encoding="utf-8"))["prints"]
want = set(int(x) for x in sys.argv[1:])
sel = [p for p in prints if p.get("hits") and (not want or p["n"] in want)]
TW = 720
PER = 4
COL = [(255, 70, 60), (70, 210, 110), (110, 170, 255)]

def tile(p):
    im = Image.open(ROOT / f"game-assets/originals/{p['slug']}.jpg").convert("RGB")
    th = round(im.height * TW / im.width); im = im.resize((TW, th))
    d = ImageDraw.Draw(im)
    for i, hb in enumerate(p["hits"]):
        x, y, w, h = hb["rect"]; c = COL[i % 3]
        for t in range(3):
            d.rectangle([x*TW+t, y*th+t, (x+w)*TW-t, (y+h)*th-t], outline=c)
        d.text((x*TW+3, y*th+3), str(i+1), fill=c)
    d.rectangle([0, 0, TW-1, th-1], outline=(120, 120, 140))
    d.text((4, 4), f"{p['n']:02d} {p['slug']}", fill=(255, 255, 0))
    # legend: labels 1/2/3
    for i, hb in enumerate(p["hits"]):
        d.text((4, 18+14*i), f"{i+1} {hb['label']}", fill=COL[i % 3])
    return im

for b in range(0, len(sel), PER):
    batch = sel[b:b+PER]; tiles = [tile(p) for p in batch]
    cols = 2; rows = math.ceil(len(tiles)/cols); pad = 8
    tw = TW; th = max(t.height for t in tiles)
    m = Image.new("RGB", (cols*tw+(cols+1)*pad, rows*th+(rows+1)*pad), (26, 26, 32))
    for i, t in enumerate(tiles):
        cx = pad+(i % cols)*(tw+pad); cy = pad+(i//cols)*(th+pad); m.paste(t, (cx, cy))
    out = OUT / f"hires-{b//PER+1}.jpg"; m.save(out, quality=90)
    print(f"{out.name}: {[p['n'] for p in batch]}")
