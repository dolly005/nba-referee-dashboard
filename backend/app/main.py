from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import get_conn
from app.sql import season_clause, game_type_clause, postseason_stage_clause
from contextlib import asynccontextmanager
from app.scheduler import start_scheduler, shutdown_scheduler
from app.admin_routes import router as admin_router


@asynccontextmanager
async def lifespan(app):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)


def _params(season: str, game_type: str, postseason_stage: str = "全部階段", **extra):
    return {"season": season, "game_type": game_type, "postseason_stage": postseason_stage, **extra}


def _conference_label(value: str | None) -> str | None:
    if value == "Eastern":
        return "East"
    if value == "Western":
        return "West"
    return value


def _normalize_conference(value: str) -> str:
    mapping = {
        "all": "all", "全部": "all", "全聯盟": "all",
        "East": "Eastern", "Eastern": "Eastern", "東區": "Eastern",
        "West": "Western", "Western": "Western", "西區": "Western",
    }
    return mapping.get(value, value)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/seasons")
def get_seasons():
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT season FROM games ORDER BY season").fetchall()
    return [row["season"] for row in rows]


@app.get("/api/game-types")
def get_game_types():
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT game_type FROM games ORDER BY game_type").fetchall()
    values = [row["game_type"] for row in rows]
    order = {"Regular Season": 0, "Playoffs": 1}
    return sorted(values, key=lambda x: order.get(x, 99))


@app.get("/api/postseason-stages")
def get_postseason_stages():
    # PostgreSQL does not allow ORDER BY expressions that are not in the
    # SELECT list when SELECT DISTINCT is used. Use GROUP BY plus a sort key.
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                postseason_stage,
                CASE postseason_stage
                    WHEN 'First Round' THEN 1
                    WHEN 'Conference Semifinals' THEN 2
                    WHEN 'Conference Finals' THEN 3
                    WHEN 'NBA Finals' THEN 4
                    ELSE 99
                END AS stage_order
            FROM games
            WHERE postseason_stage IS NOT NULL
              AND postseason_stage <> 'Regular Season'
            GROUP BY postseason_stage
            ORDER BY stage_order, postseason_stage
            """
        ).fetchall()
    return [row["postseason_stage"] for row in rows]


@app.get("/api/teams")
def get_teams():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT abbreviation, full_name, conference, division
            FROM teams
            ORDER BY conference, division, full_name
            """
        ).fetchall()
    return rows


@app.get("/api/arenas")
def get_arenas():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT a.arena_name, a.arena_name_zh, a.team_abbreviation, t.full_name AS team_name
            FROM arenas a
            JOIN teams t ON t.abbreviation = a.team_abbreviation
            ORDER BY t.conference, t.division, t.full_name
            """
        ).fetchall()
    return rows


@app.get("/api/referees/summary")

def get_referees_summary(
    season: str = Query("2021-22"),
    game_type: str = Query("Regular Season"),
    postseason_stage: str = Query("全部階段"),
):
    params = _params(season, game_type, postseason_stage)
    query = f"""
        WITH selected_games AS (
            SELECT g.*
            FROM games g
            WHERE 1=1
            {season_clause('g')}
            {game_type_clause('g')}
            {postseason_stage_clause('g')}
        ),
        game_summary AS (
            SELECT
                ROUND(
                    SUM(CASE WHEN home_win = 1 THEN 1 ELSE 0 END)::numeric
                    / NULLIF(COUNT(*), 0),
                    3
                ) AS overall_home_win_rate,
                COUNT(*)::int AS total_games,
                SUM(CASE WHEN home_win = 1 THEN 1 ELSE 0 END)::int AS home_wins,
                SUM(CASE WHEN home_win = 0 THEN 1 ELSE 0 END)::int AS home_losses
            FROM selected_games
        ),
        referee_summary AS (
            SELECT
                COUNT(DISTINCT go.official_id)::int AS total_referees
            FROM selected_games sg
            LEFT JOIN game_officials go ON go.game_id = sg.game_id
        )
        SELECT
            gs.overall_home_win_rate,
            gs.total_games,
            gs.home_wins,
            gs.home_losses,
            rs.total_referees
        FROM game_summary gs
        CROSS JOIN referee_summary rs
    """
    with get_conn() as conn:
        row = conn.execute(query, params).fetchone()
    return row or {
        "overall_home_win_rate": 0,
        "total_games": 0,
        "home_wins": 0,
        "home_losses": 0,
        "total_referees": 0,
    }


@app.get("/api/referees")
def get_referees(
    season: str = Query("2021-22"),
    game_type: str = Query("Regular Season"),
    postseason_stage: str = Query("全部階段"),
    search: Optional[str] = Query(None),
):
    params = _params(season, game_type, postseason_stage, search=f"%{search}%" if search else None)
    query = f"""
        SELECT
            go.official_id,
            go.official_name,
            COUNT(DISTINCT g.game_id)::int AS games,
            SUM(CASE WHEN g.home_win = 1 THEN 1 ELSE 0 END)::int AS home_wins,
            SUM(CASE WHEN g.home_win = 0 THEN 1 ELSE 0 END)::int AS away_wins,
            ROUND(100.0 * SUM(CASE WHEN g.home_win = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT g.game_id), 0), 1) AS home_win_rate,
            ROUND(100.0 * SUM(CASE WHEN g.home_win = 0 THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT g.game_id), 0), 1) AS away_win_rate
        FROM game_officials go
        JOIN games g ON g.game_id = go.game_id
        WHERE 1=1
        {season_clause('g')}
        {game_type_clause('g')}
        {postseason_stage_clause('g')}
        AND (%(search)s::text IS NULL OR go.official_name ILIKE %(search)s::text)
        GROUP BY go.official_id, go.official_name
        ORDER BY games DESC, go.official_name ASC
    """
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows


@app.get("/api/team-referee")
def get_team_referee(
    team: str = Query(..., min_length=2, max_length=3),
    season: str = Query("2021-22"),
    game_type: str = Query("Regular Season"),
    postseason_stage: str = Query("全部階段"),
):
    team = team.upper()
    params = _params(season, game_type, postseason_stage, team=team)
    query = f"""
        WITH selected_games AS (
            SELECT *
            FROM games g
            WHERE (%(team)s IN (g.home_team_abbreviation, g.away_team_abbreviation))
            {season_clause('g')}
            {game_type_clause('g')}
            {postseason_stage_clause('g')}
        ), team_record AS (
            SELECT
                COUNT(*)::int AS team_games,
                SUM(CASE WHEN winner_team_abbreviation = %(team)s THEN 1 ELSE 0 END)::int AS wins,
                SUM(CASE WHEN loser_team_abbreviation = %(team)s THEN 1 ELSE 0 END)::int AS losses,
                ROUND(100.0 * SUM(CASE WHEN winner_team_abbreviation = %(team)s THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS win_rate
            FROM selected_games
        )
        SELECT
            go.official_id,
            go.official_name,
            COUNT(DISTINCT sg.game_id)::int AS games,
            SUM(CASE WHEN sg.winner_team_abbreviation = %(team)s THEN 1 ELSE 0 END)::int AS wins,
            SUM(CASE WHEN sg.loser_team_abbreviation = %(team)s THEN 1 ELSE 0 END)::int AS losses,
            ROUND(100.0 * SUM(CASE WHEN sg.winner_team_abbreviation = %(team)s THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT sg.game_id), 0), 1) AS win_rate,
            (SELECT team_games FROM team_record)::int AS team_games,
            (SELECT wins FROM team_record)::int AS team_wins,
            (SELECT losses FROM team_record)::int AS team_losses,
            (SELECT win_rate FROM team_record) AS team_win_rate
        FROM selected_games sg
        JOIN game_officials go ON go.game_id = sg.game_id
        GROUP BY go.official_id, go.official_name
        ORDER BY games DESC, win_rate DESC, go.official_name ASC
    """
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows


@app.get("/api/team-stats")
def get_team_stats(
    team: str = Query(..., min_length=2, max_length=3),
    season: str = Query("2021-22"),
    game_type: str = Query("Regular Season"),
    postseason_stage: str = Query("全部階段"),
):
    team = team.upper()
    params = _params(season, game_type, postseason_stage, team=team)
    query = f"""
        WITH team_games AS (
            SELECT g.home_team_abbreviation AS team, g.home_points AS points, g.away_points AS opp_points
            FROM games g
            WHERE 1=1 {season_clause('g')} {game_type_clause('g')} {postseason_stage_clause('g')}
            UNION ALL
            SELECT g.away_team_abbreviation AS team, g.away_points AS points, g.home_points AS opp_points
            FROM games g
            WHERE 1=1 {season_clause('g')} {game_type_clause('g')} {postseason_stage_clause('g')}
        ), agg AS (
            SELECT
                tg.team,
                t.conference,
                ROUND(AVG(tg.points)::numeric, 1) AS ppg,
                ROUND(AVG(tg.opp_points)::numeric, 1) AS opp_ppg
            FROM team_games tg
            JOIN teams t ON t.abbreviation = tg.team
            GROUP BY tg.team, t.conference
        ), ranked AS (
            SELECT
                *,
                RANK() OVER (ORDER BY ppg DESC) AS ppg_rank_league,
                RANK() OVER (ORDER BY opp_ppg ASC) AS opp_ppg_rank_league,
                RANK() OVER (PARTITION BY conference ORDER BY ppg DESC) AS ppg_rank_conference,
                RANK() OVER (PARTITION BY conference ORDER BY opp_ppg ASC) AS opp_ppg_rank_conference,
                ROUND(AVG(ppg) OVER ()::numeric, 1) AS league_avg_ppg,
                ROUND(AVG(opp_ppg) OVER ()::numeric, 1) AS league_avg_opp_ppg
            FROM agg
        )
        SELECT * FROM ranked WHERE team = %(team)s
    """
    with get_conn() as conn:
        row = conn.execute(query, params).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No team stats found for current filters")
    row["conference"] = _conference_label(row.get("conference"))
    return row


@app.get("/api/arena-referee")
def get_arena_referee(
    arena: str = Query(...),
    season: str = Query("2021-22"),
    game_type: str = Query("Regular Season"),
    postseason_stage: str = Query("全部階段"),
):
    params = _params(season, game_type, postseason_stage, arena=arena.replace("+", " "))
    query = f"""
        SELECT
            go.official_id,
            go.official_name,
            COUNT(DISTINCT g.game_id)::int AS games,
            SUM(CASE WHEN g.home_win = 1 THEN 1 ELSE 0 END)::int AS home_wins,
            SUM(CASE WHEN g.home_win = 0 THEN 1 ELSE 0 END)::int AS home_losses,
            ROUND(100.0 * SUM(CASE WHEN g.home_win = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT g.game_id), 0), 1) AS home_win_rate
        FROM games g
        JOIN game_officials go ON go.game_id = g.game_id
        WHERE g.arena = %(arena)s
        {season_clause('g')}
        {game_type_clause('g')}
        {postseason_stage_clause('g')}
        GROUP BY go.official_id, go.official_name
        ORDER BY games DESC, home_win_rate DESC, go.official_name ASC
    """
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows


@app.get("/api/arena-stats")
def get_arena_stats(
    arena: str = Query(...),
    season: str = Query("2021-22"),
    game_type: str = Query("Regular Season"),
    postseason_stage: str = Query("全部階段"),
):
    params = _params(season, game_type, postseason_stage, arena=arena.replace("+", " "))
    query = f"""
        WITH home_agg AS (
            SELECT
                g.arena,
                g.home_team_abbreviation AS home_team,
                t.conference,
                COUNT(*)::int AS games,
                SUM(CASE WHEN g.home_win = 1 THEN 1 ELSE 0 END)::int AS home_wins,
                SUM(CASE WHEN g.home_win = 0 THEN 1 ELSE 0 END)::int AS home_losses,
                ROUND(SUM(CASE WHEN g.home_win = 1 THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0), 3) AS home_win_rate,
                ROUND(AVG(g.home_points)::numeric, 1) AS home_ppg,
                ROUND(AVG(g.away_points)::numeric, 1) AS home_opp_ppg
            FROM games g
            JOIN teams t ON t.abbreviation = g.home_team_abbreviation
            WHERE 1=1 {season_clause('g')} {game_type_clause('g')} {postseason_stage_clause('g')}
            GROUP BY g.arena, g.home_team_abbreviation, t.conference
        ), ranked AS (
            SELECT
                *,
                RANK() OVER (ORDER BY home_ppg DESC) AS home_ppg_rank_league,
                RANK() OVER (ORDER BY home_opp_ppg ASC) AS home_opp_ppg_rank_league,
                RANK() OVER (PARTITION BY conference ORDER BY home_ppg DESC) AS home_ppg_rank_conference,
                RANK() OVER (PARTITION BY conference ORDER BY home_opp_ppg ASC) AS home_opp_ppg_rank_conference,
                ROUND(AVG(home_ppg) OVER ()::numeric, 1) AS league_avg_home_ppg,
                ROUND(AVG(home_opp_ppg) OVER ()::numeric, 1) AS league_avg_home_opp_ppg
            FROM home_agg
        )
        SELECT * FROM ranked WHERE arena = %(arena)s
    """
    with get_conn() as conn:
        row = conn.execute(query, params).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No arena stats found for current filters")
    row["conference"] = _conference_label(row.get("conference"))
    return row


@app.get("/api/matchup-referee")
def get_matchup_referee(
    team_a: str = Query(..., min_length=2, max_length=3),
    team_b: str = Query(..., min_length=2, max_length=3),
    season: str = Query("2021-22"),
    game_type: str = Query("Regular Season"),
    postseason_stage: str = Query("全部階段"),
):
    team_a = team_a.upper()
    team_b = team_b.upper()
    if team_a == team_b:
        raise HTTPException(status_code=400, detail="team_a and team_b must be different")
    params = _params(season, game_type, postseason_stage, team_a=team_a, team_b=team_b)
    query = f"""
        SELECT
            go.official_id,
            go.official_name,
            COUNT(DISTINCT g.game_id)::int AS games,
            SUM(CASE WHEN g.winner_team_abbreviation = %(team_a)s THEN 1 ELSE 0 END)::int AS wins,
            SUM(CASE WHEN g.loser_team_abbreviation = %(team_a)s THEN 1 ELSE 0 END)::int AS losses,
            ROUND(100.0 * SUM(CASE WHEN g.winner_team_abbreviation = %(team_a)s THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT g.game_id), 0), 1) AS win_rate
        FROM games g
        JOIN game_officials go ON go.game_id = g.game_id
        WHERE (
            (g.home_team_abbreviation = %(team_a)s AND g.away_team_abbreviation = %(team_b)s)
            OR
            (g.home_team_abbreviation = %(team_b)s AND g.away_team_abbreviation = %(team_a)s)
        )
        {season_clause('g')}
        {game_type_clause('g')}
        {postseason_stage_clause('g')}
        GROUP BY go.official_id, go.official_name
        ORDER BY games DESC, win_rate DESC, go.official_name ASC
    """
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows

def _competition_rank(items, value_key, reverse=True):
    """
    Competition ranking:
    1, 2, 2, 4
    如果數值相同，名次相同，下一名會跳過。
    """
    sorted_items = sorted(
        items,
        key=lambda x: (x.get(value_key) is None, x.get(value_key) or 0),
        reverse=reverse,
    )

    rank = 0
    previous_value = None

    for index, item in enumerate(sorted_items):
        value = item.get(value_key)

        if index == 0:
            rank = 1
        elif value != previous_value:
            rank = index + 1

        item[f"{value_key}_rank"] = rank
        previous_value = value

    return sorted_items


def _apply_win_rate_rank_with_h2h(conn, teams, selected_games_sql, params):
    """
    勝率排名：
    1. 勝率不同：勝率高者在前
    2. 勝率相同且剛好兩隊：看 head-to-head
    3. head-to-head 平手：同名次
    4. 超過兩隊同勝率：先同名次處理
    """
    groups = {}

    for team in teams:
        key = team.get("win_rate")
        groups.setdefault(key, []).append(team)

    ordered = []
    current_rank = 1

    for win_rate in sorted(
        groups.keys(),
        key=lambda value: -1 if value is None else value,
        reverse=True,
    ):
        group = groups[win_rate]

        if len(group) == 1:
            group[0]["win_rate_rank"] = current_rank
            group[0]["rank_note"] = None
            ordered.extend(group)

        elif len(group) == 2:
            team_a = group[0]["team"]
            team_b = group[1]["team"]

            h2h_query = f"""
                WITH selected_games AS (
                    {selected_games_sql}
                )
                SELECT
                    SUM(
                        CASE
                            WHEN home_team_abbreviation = %(team_a)s
                              AND away_team_abbreviation = %(team_b)s
                              AND home_win = 1 THEN 1
                            WHEN away_team_abbreviation = %(team_a)s
                              AND home_team_abbreviation = %(team_b)s
                              AND home_win = 0 THEN 1
                            ELSE 0
                        END
                    )::int AS team_a_wins,
                    SUM(
                        CASE
                            WHEN home_team_abbreviation = %(team_b)s
                              AND away_team_abbreviation = %(team_a)s
                              AND home_win = 1 THEN 1
                            WHEN away_team_abbreviation = %(team_b)s
                              AND home_team_abbreviation = %(team_a)s
                              AND home_win = 0 THEN 1
                            ELSE 0
                        END
                    )::int AS team_b_wins
                FROM selected_games
                WHERE
                    (
                        home_team_abbreviation = %(team_a)s
                        AND away_team_abbreviation = %(team_b)s
                    )
                    OR
                    (
                        home_team_abbreviation = %(team_b)s
                        AND away_team_abbreviation = %(team_a)s
                    )
            """

            h2h_params = dict(params)
            h2h_params["team_a"] = team_a
            h2h_params["team_b"] = team_b

            h2h = conn.execute(h2h_query, h2h_params).fetchone()
            team_a_wins = h2h["team_a_wins"] or 0
            team_b_wins = h2h["team_b_wins"] or 0

            if team_a_wins > team_b_wins:
                group[0]["win_rate_rank"] = current_rank
                group[1]["win_rate_rank"] = current_rank + 1
                group[0]["rank_note"] = f"對戰 {team_a_wins}-{team_b_wins}"
                group[1]["rank_note"] = f"對戰 {team_b_wins}-{team_a_wins}"
                ordered.extend([group[0], group[1]])

            elif team_b_wins > team_a_wins:
                group[1]["win_rate_rank"] = current_rank
                group[0]["win_rate_rank"] = current_rank + 1
                group[1]["rank_note"] = f"對戰 {team_b_wins}-{team_a_wins}"
                group[0]["rank_note"] = f"對戰 {team_a_wins}-{team_b_wins}"
                ordered.extend([group[1], group[0]])

            else:
                group[0]["win_rate_rank"] = current_rank
                group[1]["win_rate_rank"] = current_rank
                group[0]["rank_note"] = f"對戰平手 {team_a_wins}-{team_b_wins}"
                group[1]["rank_note"] = f"對戰平手 {team_b_wins}-{team_a_wins}"
                ordered.extend(sorted(group, key=lambda x: x["team"]))

        else:
            for team in group:
                team["win_rate_rank"] = current_rank
                team["rank_note"] = "多隊同勝率，未套用完整多隊 tiebreaker"
            ordered.extend(sorted(group, key=lambda x: x["team"]))

        current_rank += len(group)

    return ordered

@app.get("/api/league-rankings")
def get_league_rankings(
    season: str = Query("2021-22"),
    game_type: str = Query("Regular Season"),
    venue: str = Query("all"),
    conference: str = Query("all"),
    postseason_stage: str = Query("全部階段"),
):
    venue = venue.lower()
    if venue not in {"all", "home", "away", "所有場次", "僅主場", "僅客場"}:
        raise HTTPException(status_code=400, detail="venue must be all, home, or away")

    venue_map = {"所有場次": "all", "僅主場": "home", "僅客場": "away"}
    venue = venue_map.get(venue, venue)
    normalized_conference = _normalize_conference(conference)

    params = _params(
        season,
        game_type,
        postseason_stage,
        venue=venue,
        conference=normalized_conference,
    )

    selected_games_sql = f"""
        SELECT *
        FROM games g
        WHERE 1=1
        {season_clause('g')}
        {game_type_clause('g')}
        {postseason_stage_clause('g')}
    """

    query = f"""
        WITH selected_games AS (
            {selected_games_sql}
        ),
        team_games AS (
            SELECT
                g.home_team_abbreviation AS team,
                CASE WHEN g.home_win = 1 THEN 1 ELSE 0 END AS win,
                CASE WHEN g.home_win = 0 THEN 1 ELSE 0 END AS loss,
                g.home_points AS points,
                g.away_points AS opp_points,
                TRUE AS is_home
            FROM selected_games g
            WHERE %(venue)s IN ('all', 'home')

            UNION ALL

            SELECT
                g.away_team_abbreviation AS team,
                CASE WHEN g.home_win = 0 THEN 1 ELSE 0 END AS win,
                CASE WHEN g.home_win = 1 THEN 1 ELSE 0 END AS loss,
                g.away_points AS points,
                g.home_points AS opp_points,
                FALSE AS is_home
            FROM selected_games g
            WHERE %(venue)s IN ('all', 'away')
        ),
        agg AS (
            SELECT
                t.abbreviation AS team,
                t.full_name,
                t.conference,
                COALESCE(SUM(tg.win), 0)::int AS wins,
                COALESCE(SUM(tg.loss), 0)::int AS losses,
                ROUND(
                    COALESCE(SUM(tg.win), 0)::numeric
                    / NULLIF(COUNT(tg.team), 0),
                    3
                ) AS win_rate,
                COALESCE(SUM(CASE WHEN tg.is_home THEN tg.win ELSE 0 END), 0)::int AS home_wins,
                COALESCE(SUM(CASE WHEN tg.is_home THEN tg.loss ELSE 0 END), 0)::int AS home_losses,
                ROUND(
                    COALESCE(SUM(CASE WHEN tg.is_home THEN tg.win ELSE 0 END), 0)::numeric
                    / NULLIF(SUM(CASE WHEN tg.is_home THEN 1 ELSE 0 END), 0),
                    3
                ) AS home_win_rate,
                ROUND(AVG(tg.points)::numeric, 1) AS ppg,
                ROUND(AVG(tg.opp_points)::numeric, 1) AS opp_ppg
            FROM teams t
            LEFT JOIN team_games tg ON tg.team = t.abbreviation
            GROUP BY t.abbreviation, t.full_name, t.conference
        )
        SELECT *
        FROM agg
        WHERE (%(conference)s = 'all' OR conference = %(conference)s)
    """

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
        teams = [dict(row) for row in rows]

        for team in teams:
            team["conference"] = _conference_label(team.get("conference"))

        # 得分排名：高者排名前，同分同名次，下一名跳過。
        ppg_ranked = _competition_rank([dict(team) for team in teams], "ppg", reverse=True)
        ppg_rank_map = {team["team"]: team["ppg_rank"] for team in ppg_ranked}

        # 失分排名：低者排名前，同分同名次，下一名跳過。
        opp_ppg_ranked = _competition_rank([dict(team) for team in teams], "opp_ppg", reverse=False)
        opp_ppg_rank_map = {team["team"]: team["opp_ppg_rank"] for team in opp_ppg_ranked}

        # 勝率排名：同勝率兩隊時，用 head-to-head；若平手，則同名。
        win_rate_ranked = _apply_win_rate_rank_with_h2h(conn, teams, selected_games_sql, params)

    for team in win_rate_ranked:
        team["ppg_rank"] = ppg_rank_map.get(team["team"])
        team["opp_ppg_rank"] = opp_ppg_rank_map.get(team["team"])

    return {"teams": win_rate_ranked}
