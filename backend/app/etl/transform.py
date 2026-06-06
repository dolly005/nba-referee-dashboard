from __future__ import annotations

from datetime import date
import pandas as pd


def _safe_get(row: pd.Series, *keys, default=None):
    for key in keys:
        if key in row and pd.notna(row[key]):
            return row[key]
    return default


def _to_int(value):
    if value is None or pd.isna(value):
        return None
    try:
        return int(value)
    except Exception:
        return None


def transform_games(games_raw: pd.DataFrame, target_date: date) -> pd.DataFrame:
    """
    LeagueGameLog 原本是一隊一列。
    這裡整理成一場比賽一列，符合你的 games 資料表。
    """
    if games_raw.empty:
        return pd.DataFrame()

    games: list[dict] = []

    for game_id, group in games_raw.groupby("GAME_ID"):
        group = group.copy()

        home_row = None
        away_row = None

        for _, row in group.iterrows():
            matchup = str(_safe_get(row, "MATCHUP", default=""))

            if " vs. " in matchup:
                home_row = row
            elif " @ " in matchup:
                away_row = row

        if home_row is None or away_row is None:
            rows = list(group.iterrows())
            if len(rows) >= 2:
                home_row = rows[0][1]
                away_row = rows[1][1]
            else:
                continue

        home_points = _to_int(_safe_get(home_row, "PTS", default=None))
        away_points = _to_int(_safe_get(away_row, "PTS", default=None))

        home_team_id = _to_int(_safe_get(home_row, "TEAM_ID", default=None))
        away_team_id = _to_int(_safe_get(away_row, "TEAM_ID", default=None))

        home_win = None
        winner_team_id = None
        winner_team_abbreviation = None
        loser_team_id = None
        loser_team_abbreviation = None

        home_team_abbreviation = _safe_get(home_row, "TEAM_ABBREVIATION", default=None)
        away_team_abbreviation = _safe_get(away_row, "TEAM_ABBREVIATION", default=None)

        if home_points is not None and away_points is not None:
            if home_points > away_points:
                home_win = 1
                winner_team_id = home_team_id
                winner_team_abbreviation = home_team_abbreviation
                loser_team_id = away_team_id
                loser_team_abbreviation = away_team_abbreviation
            else:
                home_win = 0
                winner_team_id = away_team_id
                winner_team_abbreviation = away_team_abbreviation
                loser_team_id = home_team_id
                loser_team_abbreviation = home_team_abbreviation

        game_type = _safe_get(home_row, "SEASON_TYPE", default="Regular Season")

        games.append({
            "game_id": _to_int(game_id),
            "game_date": target_date,
            "season": _safe_get(home_row, "NBA_SEASON", default=None),
            "game_type": game_type,
            "arena": None,

            "home_team_id": home_team_id,
            "home_team_abbreviation": home_team_abbreviation,
            "home_team_name": _safe_get(home_row, "TEAM_NAME", default=None),
            "home_points": home_points,

            "away_team_id": away_team_id,
            "away_team_abbreviation": away_team_abbreviation,
            "away_team_name": _safe_get(away_row, "TEAM_NAME", default=None),
            "away_points": away_points,

            "home_win": home_win,
            "winner_team_id": winner_team_id,
            "winner_team_abbreviation": winner_team_abbreviation,
            "loser_team_id": loser_team_id,
            "loser_team_abbreviation": loser_team_abbreviation,
            "neutral_site": 0,
        })

    return pd.DataFrame(games)


def _normalize_official_id(row: pd.Series):
    raw = _safe_get(
        row,
        "OFFICIAL_ID",
        "official_id",
        "PERSON_ID",
        "personId",
        "person_id",
        "PERSONID",
        default=None,
    )
    return _to_int(raw)


def _normalize_first_name(row: pd.Series):
    first = _safe_get(
        row,
        "FIRST_NAME",
        "firstName",
        "FIRSTNAME",
        "first_name",
        default=None,
    )
    return str(first).strip() if first is not None else None


def _normalize_last_name(row: pd.Series):
    last = _safe_get(
        row,
        "LAST_NAME",
        "lastName",
        "LASTNAME",
        "last_name",
        default=None,
    )
    return str(last).strip() if last is not None else None


def _normalize_official_name(row: pd.Series) -> str | None:
    direct_name = _safe_get(
        row,
        "OFFICIAL_NAME",
        "official_name",
        "name",
        "NAME",
        default=None,
    )
    if direct_name:
        return str(direct_name).strip()

    first_name = _normalize_first_name(row) or ""
    last_name = _normalize_last_name(row) or ""

    full_name = f"{first_name} {last_name}".strip()
    return full_name if full_name else None


def transform_game_officials(officials_raw: pd.DataFrame) -> pd.DataFrame:
    """
    整理成你的 game_officials 資料表格式。
    """
    if officials_raw.empty:
        return pd.DataFrame()

    rows: list[dict] = []

    for _, row in officials_raw.iterrows():
        game_id = _to_int(_safe_get(row, "GAME_ID", "game_id", default=None))
        official_id = _normalize_official_id(row)
        official_name = _normalize_official_name(row)

        if game_id is None or official_id is None or not official_name:
            continue

        first_name = _normalize_first_name(row)
        last_name = _normalize_last_name(row)

        jersey_num = _to_int(_safe_get(
            row,
            "JERSEY_NUM",
            "jerseyNum",
            "JERSEYNUM",
            "jersey_num",
            default=None,
        ))

        rows.append({
            "game_id": game_id,
            "official_id": official_id,
            "official_name": official_name,
            "first_name": first_name,
            "last_name": last_name,
            "jersey_num": jersey_num,
        })

    return pd.DataFrame(rows).drop_duplicates(
        subset=["game_id", "official_id"]
    )


def transform_daily_data(raw_data: dict) -> dict[str, pd.DataFrame]:
    games_df = transform_games(raw_data["games_raw"], raw_data["target_date"])
    game_officials_df = transform_game_officials(raw_data["officials_raw"])

    return {
        "games": games_df,
        "game_officials": game_officials_df,
    }