# NBA Referee Dashboard — Regular Season + Playoffs version

這一版已把原本只有例行賽的資料替換為「例行賽 + 季後賽」合併資料，並修改前後端讓網站可以用賽事類別切換：全部賽事、例行賽、季後賽。

## 本版資料

`data/` 資料夾內有四個檔案：

- `nba_games_regular_playoffs_2021_2026.csv`
- `nba_game_officials_regular_playoffs_2021_2026.csv`
- `nba_games_with_officials_regular_playoffs_2021_2026.csv`
- `merge_validation_summary.csv`

為了保留舊程式或舊路徑相容性，專案根目錄下的三個舊檔名也已經換成合併後資料：

- `nba_games_2021_2026.csv`
- `nba_game_officials_2021_2026.csv`
- `nba_games_with_officials_2021_2026.csv`

資料量：

| dataset | rows | unique games |
|---|---:|---:|
| games | 6,569 | 6,569 |
| officials | 19,960 | 6,569 |
| games_with_officials | 19,960 | 6,569 |

其中 games = 6,150 場例行賽 + 419 場季後賽；officials = 18,451 筆例行賽裁判場次 + 1,509 筆季後賽裁判場次。

## 主要修改位置

### 後端

1. `backend/sql/001_init.sql`
   - `games` 新增：`season_type`、`postseason_stage`、`postseason_season_type`、`special_site`。
   - `game_officials` 新增：`season_type`、`postseason_stage`、`postseason_season_type`、`special_site`。

2. `backend/scripts/import_csv.py`
   - 不再把所有比賽強制設為 `Regular Season`。
   - 改用 CSV 裡的 `SEASON_TYPE` 匯入 `game_type`，所以會有 `Regular Season` 與 `Playoffs`。
   - 支援合併後的新欄位。

3. `backend/app/sql.py`
   - `game_type` 支援 `全部賽事` / `All games`，不只單一類別。

4. `backend/app/main.py`
   - 新增 `/api/game-types`，讓前端可以自動取得目前資料庫內的賽事類別。
   - 新增 `/api/postseason-stages`，目前先保留給之後若要細分第一輪、第二輪、分區冠軍賽、總冠軍賽使用。

### 前端

1. `frontend/src/components/Filters.jsx`
   - 原本「季後賽」按鈕是 disabled。
   - 現在改成可點選：`全部賽事`、`例行賽`、`季後賽`。

2. `frontend/src/App.jsx`
   - 啟動時多抓 `/api/game-types`。

3. 四個頁面都已接上新的 `gameTypes`：
   - `RefereesPage.jsx`
   - `TeamRefereePage.jsx`
   - `ArenaRefereePage.jsx`
   - `MatchupRefereePage.jsx`

## 執行方式

以下假設你已經有 PostgreSQL，而且 `.env` 的 `DATABASE_URL` 已設定好。

### 1. 後端初始化資料庫

在第一個 Terminal：

```bash
cd nba-referee-dashboard-full-merged/backend
source .venv/bin/activate  # 如果你還沒建立 venv，先看下方「重新建立環境」
psql "$DATABASE_URL" -f sql/001_init.sql
python scripts/import_csv.py \
  --games ../data/nba_games_regular_playoffs_2021_2026.csv \
  --officials ../data/nba_game_officials_regular_playoffs_2021_2026.csv
uvicorn app.main:app --reload --port 8000
```

如果你的 `.env` 有 `DATABASE_URL`，但 shell 裡沒有，可改成：

```bash
export $(grep -v '^#' .env | xargs)
psql "$DATABASE_URL" -f sql/001_init.sql
```

### 2. 後端測試

後端成功後，測這幾個：

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/seasons
curl http://localhost:8000/api/game-types
curl "http://localhost:8000/api/referees?season=2021-22&game_type=Playoffs"
```

預期：

- `/api/health` 回傳 `{"status":"ok"}`。
- `/api/game-types` 應包含 `Regular Season` 與 `Playoffs`。
- `game_type=Playoffs` 會回傳季後賽裁判資料。

### 3. 前端啟動

在第二個 Terminal：

```bash
cd nba-referee-dashboard-full-merged/frontend
npm install
npm run dev
```

打開：

```text
http://localhost:5173
```

## 目前網站具備功能

目前前端有四個主要頁面：

1. 裁判名單：依賽季與賽事類別彙總每位裁判吹判場次、主場勝率、客場勝率。
2. 球隊 × 裁判：選定球隊後，查看該球隊在不同裁判執法時的勝敗與勝率。
3. 場館 × 裁判：選定主場場館後，查看該場館在不同裁判執法時的主隊勝率。
4. 對戰組合 × 裁判：選定兩隊後，查看特定對戰組合下，不同裁判執法時球隊 A 的勝敗與勝率。

每頁都可以切換：

- 單一賽季或所有賽季
- 全部賽事、例行賽、季後賽

## 目前限制

1. `postseason_stage` 已匯入資料庫，但前端還沒有做「第一輪 / 第二輪 / 分區冠軍賽 / 總冠軍賽」的細分篩選器。
2. 資料來源目前不含附加賽；本版只處理例行賽與季後賽。
3. 場館分析仍以主隊對應主場作為場館歸類；中立場或特殊場地已用 `neutral_site` / `special_site` 標記，但前端尚未另外做特殊場地篩選。
4. `POST /api/admin/refresh-data` 是原本的單日補資料功能，這次沒有完整改造成「可自動重建例行賽 + 季後賽整包資料」。本次主要是替換靜態 CSV 與匯入流程。

## 重新建立後端環境

如果壓縮檔內沒有 `.venv`，請用：

```bash
cd nba-referee-dashboard-full-merged/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
