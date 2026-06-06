# 新增功能版說明

這個版本已把網站改成支援「例行賽 + 季後賽合併資料」，並新增季後賽階段篩選器與聯盟排名頁。

## 新增後端 API

- `GET /api/postseason-stages`
- `GET /api/referees/summary?season=2021-22&game_type=Regular+Season&postseason_stage=全部階段`
- `GET /api/team-stats?team=BOS&season=2021-22&game_type=Regular+Season&postseason_stage=全部階段`
- `GET /api/arena-stats?arena=TD+Garden&season=2021-22&game_type=Regular+Season&postseason_stage=全部階段`
- `GET /api/league-rankings?season=2021-22&game_type=Regular+Season&venue=all&conference=all&postseason_stage=全部階段`

原本四個主要 API 也已加入 `postseason_stage` 參數：

- `/api/referees`
- `/api/team-referee`
- `/api/arena-referee`
- `/api/matchup-referee`

## 新增前端功能

1. 所有主要頁面可依季後賽階段篩選：
   - 第一輪
   - 第二輪／Conference Semifinals
   - 分區冠軍賽
   - 總冠軍賽

2. 裁判名單頁新增 Summary Banner：
   - 本賽季聯盟整體主場勝率
   - 主場 W-L 與總場次
   - 裁判數與比賽數

3. 球隊 × 裁判頁新增場均數據面板：
   - PPG
   - Opp PPG
   - 與聯盟平均差值
   - 聯盟排名
   - 分區排名

4. 場館 × 裁判頁新增主場數據面板：
   - 主場勝率
   - Home PPG
   - Home Opp PPG
   - 與聯盟主場平均差值
   - 聯盟排名
   - 分區排名

5. 新增「聯盟排名」頁：
   - 球隊勝率排名
   - 場均得分排名
   - 場均失分排名
   - 支援賽季、賽事類別、季後賽階段、主客場、東西區篩選

6. 球隊選擇器改為 NBA 官方 Logo 顯示。

## 尚未加入的項目

目前資料檔沒有 `FTA`、`FTM`、`PF`、`FOULS` 等欄位，因此「場均罰球」與「場均犯規」無法從現有 CSV 精確計算。若之後補入 box score/team stats 資料，可以再把這兩欄加回裁判名單表格。

## 執行方式

### 後端

```bash
cd nba-referee-dashboard-full-merged/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

確認 `.env` 裡的 `DATABASE_URL` 正確後：

```bash
export $(grep -v '^#' .env | xargs)
psql "$DATABASE_URL" -f sql/001_init.sql
python scripts/import_csv.py \
  --games ../data/nba_games_regular_playoffs_2021_2026.csv \
  --officials ../data/nba_game_officials_regular_playoffs_2021_2026.csv
uvicorn app.main:app --reload --port 8000
```

### 前端

另開一個 Terminal：

```bash
cd nba-referee-dashboard-full-merged/frontend
npm install
npm run dev
```

瀏覽器開啟：

```text
http://localhost:5173
```
