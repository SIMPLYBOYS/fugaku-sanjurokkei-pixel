#!/usr/bin/env python3
"""把館藏地圖掃描處理成 overworld 底圖:裁邊 → 拉飽和 → 調暗 → 縮放。
用法:
  python3 tools/make-overworld.py --crop L,T,R,B [--sat 1.3] [--dark 0.75] [--width 3200] [--preview]
--crop  各邊裁掉比例 (0–0.5),先去館藏襯板/色卡/量尺,再聚焦到有視點的中東部
--preview  只輸出到 $TMPDIR/ow-preview.jpg 供檢視,不動 game-assets
"""
import os, argparse
from pathlib import Path
from PIL import Image, ImageEnhance
Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs/overworld-candidates/3-japan-mountains-seas-map.jpg"

ap = argparse.ArgumentParser()
ap.add_argument("--crop", required=True, help="L,T,R,B 比例")
ap.add_argument("--sat", type=float, default=1.35)
ap.add_argument("--dark", type=float, default=0.72)
ap.add_argument("--width", type=int, default=3200)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()

im = Image.open(SRC).convert("RGB")
w, h = im.size
l, t, r, b = (float(x) for x in a.crop.split(","))
im = im.crop((int(w*l), int(h*t), int(w*(1-r)), int(h*(1-b))))
if a.sat != 1.0:  im = ImageEnhance.Color(im).enhance(a.sat)
if a.dark != 1.0: im = ImageEnhance.Brightness(im).enhance(a.dark)
tw = min(a.width, im.width)
im = im.resize((tw, round(im.height*tw/im.width)), Image.Resampling.LANCZOS)

if a.preview:
    out = Path(os.environ.get("TMPDIR", "/tmp")) / "ow-preview.jpg"
else:
    out = ROOT / "game-assets/overworld.jpg"; out.parent.mkdir(parents=True, exist_ok=True)
im.save(out, quality=82)
print(f"{out}  {im.size}  {out.stat().st_size//1024}KB")
