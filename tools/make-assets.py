#!/usr/bin/env python3
"""從 assets/{slug}.jpg 產出三種遊戲資產:
  game-assets/originals/{slug}.jpg  1000px 寬（卡片主圖）
  game-assets/large/{slug}.jpg      2600px 寬（全螢幕檢視,不超采樣）
  game-assets/scenes/{slug}.png     320px 寬、量化到富嶽色盤（像素場景）

用法: python3 tools/make-assets.py 01-kanagawa-oki-namiura [--crop L,T,R,B]
--crop 為去紙邊的比例（各邊裁掉的分數,如 0.02,0.02,0.02,0.02）
"""
import json, argparse
from pathlib import Path
from PIL import Image

LANCZOS = Image.Resampling.LANCZOS
ROOT = Path(__file__).resolve().parent.parent
PALETTE = [tuple(int(c[i:i+2], 16) for i in (1, 3, 5))
           for c in json.load(open(ROOT / "assets/palette.json"))["colors"]]


def quantize(im):
    p = Image.new("P", (1, 1))
    flat = [v for c in PALETTE for v in c]
    p.putpalette(flat + flat[:3] * (256 - len(PALETTE)))
    return im.convert("RGB").quantize(palette=p, dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--crop", help="L,T,R,B 各邊裁掉比例 (0–0.5)")
    args = ap.parse_args()

    src = ROOT / f"assets/{args.slug}.jpg"
    im = Image.open(src).convert("RGB")
    if args.crop:
        l, t, r, b = (float(x) for x in args.crop.split(","))
        w, h = im.size
        im = im.crop((int(w * l), int(h * t), int(w * (1 - r)), int(h * (1 - b))))

    def rw(width):
        return im.resize((width, round(im.height * width / im.width)), LANCZOS)

    for sub in ("originals", "large", "scenes"):
        (ROOT / "game-assets" / sub).mkdir(parents=True, exist_ok=True)
    o = ROOT / f"game-assets/originals/{args.slug}.jpg"
    lg = ROOT / f"game-assets/large/{args.slug}.jpg"
    sc = ROOT / f"game-assets/scenes/{args.slug}.png"
    rw(min(1000, im.width)).save(o, quality=85)
    rw(min(2600, im.width)).save(lg, quality=78)
    quantize(rw(320)).save(sc, optimize=True)
    for p in (o, lg, sc):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
