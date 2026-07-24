# 冨嶽三十六景 ピクセル — Fugaku Pixel

**在北斎《冨嶽三十六景》的浮世繪真跡裡找細節——單一 HTML 檔的隱藏物件遊戲。**

[Tōkaidō Pixel](https://github.com/SIMPLYBOYS/tokaido-pixel) 系列的富士篇。同一套公式：一張古地圖當 overworld，每個視點進到像素化的浮世繪裡找三個藏在畫中的細節，找齊解鎖美術館高清原圖。

沒有框架、沒有建置步驟、沒有伺服器邏輯。一個 `index.html`、公有領域畫作、你的瀏覽器。

## 快速開始

```bash
python3 -m http.server 8797
# 開 http://localhost:8797
```

任何靜態伺服器皆可（需經 HTTP 開啟，`index.html` 會 `fetch` 讀取 `data/prints.json`）。

## 玩法

- overworld 是一張江戶期的日本古地圖，**富士居中**，46 個視點按**真實地理**散在中東部本州上。
- **點金色脈動的節點**進入該景的像素場景。
- **找出畫面下方列出的 3 個細節**（點畫面；命中會框住並標名）。
- 三個全找到，**解鎖該幅的美術館高清原圖**（含視點與出典，並提示「富士はどこに」）。
- **図鑑 ZUKAN**：已解鎖的收藏簿。
- **絵巻 EMAKI**：把已解鎖的原圖接成一條橫向繪卷，右→左展開（可自動）。
- **証書 CERT**：畫布繪製的完破之証（青海波邊框、雅號、朱印），可存成 PNG。
- **🔊**：原創 Web Audio 陽音階小調配樂，可開關。
- 進度存在 `localStorage`，載入後可離線遊玩。

## 內容

- **全 46 幅** — 表富士 36 + 裏富士 10（追加），每幅 3 個隱藏細節，共 **138 個**，逐幅在真跡上標定並核對。
- **每幅兩種呈現** — 320px、量化到 16 色浮世繪色盤（Floyd–Steinberg 抖動）的像素場景，以及美術館高清原圖。
- **地理 overworld** — 石川流宣《日本海山潮陸図》(1691) 為底，節點按令制國/地物落在真實位置。

## 畫作與授權

全部 **public domain**（北斎歿 1849）。逐幅出處見 [`assets/sources.json`](assets/sources.json)。

- **各景（場景／原圖）** — 葛飾北斎《冨嶽三十六景》，來源 **The Metropolitan Museum of Art**，Open Access / **CC0**（46/46 全數）。備援：芝加哥藝術學院（全套 CC0）、Wikimedia。
- **overworld 底圖** — 石川流宣《日本海山潮陸図》，來源 **國立國會圖書館（NDL）**，**Public Domain Mark**。

> 像素場景是對掃描的改作；原圖為忠實縮放、未改色。overworld 底圖經裁切與明度/飽和調整。

## 資產管線（[`tools/`](tools/)）

| 工具 | 作用 |
|---|---|
| `fetch-met.py` | 依 `data/prints.json` 從 Met Open Access 抓原圖 |
| `extract-palette.py` | k-means/median-cut 抽 16 色富嶽色盤 → `assets/palette.json` |
| `make-assets.py` | 產出 scenes(320px 量化) / originals(1000px) / large(2600px) |
| `make-overworld.py` | 館藏地圖 → 裁邊/調色 → `game-assets/overworld.jpg` |
| `qa-hits.py` | 把細節框畫在場景上,拼圖供人工核對 |

## 資料

[`data/prints.json`](data/prints.json) 是單一真實來源：每幅含編號、令制國視點、Met 藏品編號、overworld 地理座標 `pos`、3 個細節框 `hits`、適用性評估 `suit`。

## 開發紀錄

- [`docs/phase0-asset-survey.md`](docs/phase0-asset-survey.md) — 素材普查與逐幅適用性評估。
- [`docs/overworld-candidates/`](docs/overworld-candidates/) — overworld 底圖候選與選擇理由。
