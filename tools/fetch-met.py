#!/usr/bin/env python3
"""從 Met Open Access 抓富嶽三十六景原圖到 assets/{slug}.jpg。

用法:
  python3 tools/fetch-met.py 01-kanagawa-oki-namiura 02-gaifu-kaisei   # 指定 slug
  python3 tools/fetch-met.py --all                                     # 全 46 幅
已存在的檔案跳過。來源: collectionapi.metmuseum.org (primaryImage 全解析)。
"""
import json, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRINTS = {p["slug"]: p for p in json.load(open(ROOT / "data/prints.json", encoding="utf-8"))["prints"]}
API = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"
UA = {"User-Agent": "fugaku-pixel/0.1 (public-domain art pipeline)"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binary else json.loads(r.read())


def fetch(slug):
    pr = PRINTS[slug]
    out = ROOT / f"assets/{slug}.jpg"
    if out.exists():
        print(f"skip  {slug}  ({out.stat().st_size // 1024}KB)")
        return
    meta = get(API.format(pr["met_obj"]))
    if not meta.get("isPublicDomain"):
        print(f"WARN  {slug}  obj {pr['met_obj']} not flagged public domain")
    img_url = meta.get("primaryImage") or meta.get("primaryImageSmall")
    if not img_url:
        print(f"FAIL  {slug}  no image url on obj {pr['met_obj']}")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(get(img_url, binary=True))
    print(f"got   {slug}  {out.stat().st_size // 1024}KB  <- {img_url.split('/')[-1]}")


def main():
    args = sys.argv[1:]
    slugs = list(PRINTS) if "--all" in args else args
    if not slugs:
        sys.exit(__doc__)
    for s in slugs:
        if s not in PRINTS:
            print(f"?     {s}  not in prints.json")
            continue
        try:
            fetch(s)
        except Exception as e:
            print(f"ERR   {s}  {e}")


if __name__ == "__main__":
    main()
