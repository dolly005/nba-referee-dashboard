# NBA Referee Dashboard

React + Tailwind CSS 前端、FastAPI 後端、PostgreSQL 資料庫的 NBA 裁判分析儀表板。

此專案支援四個頁面：

1. 裁判名單
2. 球隊 × 裁判
3. 場館 × 裁判
4. 對戰組合 × 裁判

所有 API 都會依 `season` 與 `game_type` 篩選，不會把所有賽季混在一起。前端保留「季後賽」UI，但按鈕設為 disabled。

---

## 1. 專案資料夾結構

```text
nba-referee-dashboard-full/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── main.py
│   │   └── sql.py
│   ├── scripts/
│   │   └── import_csv.py
│   ├── sql/
│   │   └── 001_init.sql
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js
│   │   ├── components/
│   │   ├── data/teamMeta.js
│   │   ├── pages/
│   │   ├── utils/format.js
│   │   ├── App.jsx
│   │   ├── hooks.js
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   └── tailwind.config.js
├── .gitignore
└── README.md
```

---

## 2. 本機資料庫設定

### 2.1 建立 PostgreSQL database

```bash
createdb nba_referees
```

若你的 PostgreSQL 使用者不是預設帳號，請自行調整連線字串。

### 2.2 執行 migration

```bash
cd backend
psql "postgresql://postgres:postgres@localhost:5432/nba_referees" -f sql/001_init.sql
```

這個 SQL 會建立並初始化：

- `teams`
- `arenas`
- `games`
- `game_officials`

---

## 3. 匯入你爬好的 CSV

你目前有兩個主要 CSV：

- `nba_games_2021_2026.csv`
- `nba_game_officials_2021_2026.csv`

建議先把這兩個 CSV 放在專案根目錄或 `backend/data/`，然後執行：

```bash
cd backend
cp .env.example .env
```

打開 `backend/.env`，確認：

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nba_referees
CORS_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
```

安裝 Python 套件：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

匯入資料：

```bash
python scripts/import_csv.py \
  --games ../nba_games_2021_2026.csv \
  --officials ../nba_game_officials_2021_2026.csv
```

若你的 CSV 放在其他位置，請把路徑改成你的實際路徑。

注意：你提供的 `nba_games_2021_2026.csv` 沒有場館欄位，因此 `import_csv.py` 會依主場球隊自動填入規格中指定的場館。若未來你有真實 historical arena 欄位，可以在 import script 中改成使用 CSV 內的 arena 欄位。

---

## 4. 啟動 FastAPI 後端

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API 文件：

```text
http://localhost:8000/docs
```

可測試：

```text
http://localhost:8000/api/referees?season=2021-22&game_type=Regular%20Season
http://localhost:8000/api/team-referee?team=BOS&season=2021-22&game_type=Regular%20Season
http://localhost:8000/api/arena-referee?arena=TD%20Garden&season=2021-22&game_type=Regular%20Season
http://localhost:8000/api/matchup-referee?team_a=BOS&team_b=LAL&season=2021-22&game_type=Regular%20Season
http://localhost:8000/api/seasons
http://localhost:8000/api/teams
```

---

## 5. 啟動 React 前端

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

確認 `frontend/.env`：

```env
VITE_API_BASE_URL=http://localhost:8000
```

開啟：

```text
http://localhost:5173
```

---

## 6. 前端功能說明

### 共用功能

每頁都有：

- 賽季選擇器：含「所有賽季」與資料庫內可用賽季
- 賽事類別選擇器：例行賽可選，季後賽 disabled
- 顯著賽季 pill
- Skeleton loader
- Empty state
- 可排序表格
- 前三名列高亮
- 深海軍藍、白色、NBA 紅色重點色

### 頁面一：裁判名單

API：`GET /api/referees`

欄位：

- 裁判姓名
- 吹判場次
- 主場勝率
- 客場勝率

支援搜尋裁判姓名。

### 頁面二：球隊 × 裁判

API：`GET /api/team-referee`

勝負以所選球隊視角計算，不分主客場。頂部大卡顯示該球隊在目前賽季的總勝率。

### 頁面三：場館 × 裁判

API：`GET /api/arena-referee`

勝負以該場館「主隊」視角計算。

### 頁面四：對戰組合 × 裁判

API：`GET /api/matchup-referee`

查詢條件：

```sql
(home_team = team_a AND away_team = team_b)
OR
(home_team = team_b AND away_team = team_a)
```

表格以 Team A 視角呈現勝、敗與勝率。

---

## 7. 部署說明

### 7.1 後端部署到 Railway 或 Render

環境變數：

```env
DATABASE_URL=你的 PostgreSQL connection string
CORS_ORIGINS=https://你的-vercel-domain.vercel.app
```

啟動指令：

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

部署後要先在遠端 PostgreSQL 執行：

```bash
psql "$DATABASE_URL" -f backend/sql/001_init.sql
python backend/scripts/import_csv.py --games path/to/nba_games_2021_2026.csv --officials path/to/nba_game_officials_2021_2026.csv
```

若 Railway/Render 不方便直接上傳 CSV，可以先在本機匯入遠端 DB，只要 `DATABASE_URL` 指向遠端資料庫即可。

### 7.2 前端部署到 Vercel

Vercel 專案設定：

- Framework Preset：Vite
- Root Directory：`frontend`
- Build Command：`npm run build`
- Output Directory：`dist`

環境變數：

```env
VITE_API_BASE_URL=https://你的後端網址
```

---

## 8. 重要資料設計說明

### 為什麼分成 games 與 game_officials？

一場比賽會有多位裁判，因此是：

- `games`：一場比賽一列
- `game_officials`：一位裁判吹一場比賽一列

這樣才能正確統計「每位裁判出現在哪些比賽」。

### 為什麼每個 API 都要傳 season？

因為你的核心限制是不可混合不同賽季。SQL 都有：

```sql
AND (g.season = %(season)s OR %(season)s IN ('All', 'All seasons', '所有賽季'))
AND g.game_type = %(game_type)s
```

所以選單選單一賽季時只會查該賽季；選「所有賽季」才會跨季統計。

---

## 9. 後續可擴充項目

1. 加入真實 NBA logo 圖檔，而不是目前的縮寫 badge。
2. 增加裁判詳細頁，顯示該裁判各季吹判趨勢。
3. 加入 Recharts 圖表，例如裁判主場勝率分布圖。
4. 未來若爬到季後賽資料，只要將 games.game_type 匯入為 `Playoffs`，並移除前端季後賽按鈕 disabled 即可。
