from __future__ import annotations

import time
from datetime import date
from typing import Any

import pandas as pd
import requests
from nba_api.stats.endpoints import gamerotation

# BoxScoreSummaryV3 在新版 nba_api 才有；若本機版本沒有，下面會自動 fallback 到 V2
try:
    from nba_api.stats.endpoints import boxscoresummaryv3
except Exception:
    boxscoresummaryv3 = None

from nba_api.stats.endpoints import boxscoresummaryv2


NBA_HEADERS = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/stats/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}

NBA_STATS_PAGE_URL = "https://www.nba.com/stats"
LEAGUE_GAME_LOG_URL = "https://stats.nba.com/stats/leaguegamelog"
BOX_SCORE_SUMMARY_V2_URL = "https://stats.nba.com/stats/boxscoresummaryv2"

def get_nba_season(target_date: date) -> str:
    """
    NBA season 格式：2024-25
    10、11、12 月屬於當年度開季；1~9 月屬於前一年度開季。
    """
    if target_date.month >= 10:
        start_year = target_date.year
    else:
        start_year = target_date.year - 1

    end_year_short = str(start_year + 1)[-2:]
    return f"{start_year}-{end_year_short}"

def _fetch_league_game_log_direct(
    session: requests.Session,
    season: str,
    season_type: str,
    target_date: date,
) -> pd.DataFrame:
    """
    Directly request stats.nba.com LeagueGameLog.

    This is more stable than nba_api.LeagueGameLog in some network environments
    because we warm up the NBA stats page first and keep the same session/cookies.
    """
    date_str = target_date.strftime("%m/%d/%Y")

    params = {
        "Counter": "0",
        "DateFrom": date_str,
        "DateTo": date_str,
        "Direction": "ASC",
        "LeagueID": "00",
        "PlayerOrTeam": "T",
        "Season": season,
        "SeasonType": season_type,
        "Sorter": "DATE",
    }

    response = session.get(
        LEAGUE_GAME_LOG_URL,
        headers=NBA_HEADERS,
        params=params,
        timeout=(10, 180),
    )

    response.raise_for_status()

    data = response.json()
    result_sets = data.get("resultSets", [])

    if not result_sets:
        return pd.DataFrame()

    first_result = result_sets[0]
    columns = first_result.get("headers", [])
    rows = first_result.get("rowSet", [])

    if not columns or not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=columns)
    df["SEASON_TYPE"] = season_type
    df["NBA_SEASON"] = season

    return df

def extract_league_games(target_date: date) -> pd.DataFrame:
    """
    抓指定日期的例行賽 + 季後賽比賽。

    This version uses requests.Session + NBA stats page warm-up.
    It avoids timeout issues that may happen when using nba_api.LeagueGameLog directly.
    """
    season = get_nba_season(target_date)

    print(f"[extract_league_games] target_date={target_date}, season={season}")

    session = requests.Session()

    try:
        warm_response = session.get(
            NBA_STATS_PAGE_URL,
            headers={
                "User-Agent": NBA_HEADERS["User-Agent"],
                "Accept-Language": NBA_HEADERS["Accept-Language"],
            },
            timeout=(10, 60),
        )
        print(f"[extract_league_games] Warm-up status: {warm_response.status_code}")

    except Exception as exc:
        raise RuntimeError(f"NBA stats page warm-up failed: {exc}")

    time.sleep(3)

    all_frames: list[pd.DataFrame] = []
    errors: list[str] = []

    for season_type in ["Regular Season", "Playoffs"]:
        try:
            df = _fetch_league_game_log_direct(
                session=session,
                season=season,
                season_type=season_type,
                target_date=target_date,
            )

            if not df.empty:
                df["GAME_DATE_PARSED"] = pd.to_datetime(
                    df["GAME_DATE"],
                    errors="coerce",
                ).dt.date

                df = df[df["GAME_DATE_PARSED"] == target_date].copy()

                if not df.empty:
                    all_frames.append(df)
                    print(
                        f"[extract_league_games] {season_type}: "
                        f"{df['GAME_ID'].nunique()} games, {len(df)} rows"
                    )
                else:
                    print(f"[extract_league_games] {season_type}: no rows after date filter")
            else:
                print(f"[extract_league_games] {season_type}: empty response")

            time.sleep(1)

        except Exception as exc:
            message = f"{season_type} failed: {type(exc).__name__}: {exc}"
            print(f"[extract_league_games] {message}")
            errors.append(message)

    if not all_frames:
        error_text = "; ".join(errors) if errors else "No games returned by NBA Stats API."
        raise RuntimeError(
            f"No games extracted for {target_date}, season={season}. {error_text}"
        )

    result = pd.concat(all_frames, ignore_index=True)

    print(
        f"[extract_league_games] Found {result['GAME_ID'].nunique()} games "
        f"for {target_date}, rows={len(result)}"
    )

    return result

def extract_game_rotation(game_id: str) -> dict[str, pd.DataFrame]:
    """
    GameRotation 是球員輪替資料，不是裁判資料。
    這裡保留是為了符合 pipeline 說明，也可作為未來擴充。
    目前 dashboard 不一定會用到。
    """
    try:
        endpoint = gamerotation.GameRotation(
            game_id=game_id,
            headers=NBA_HEADERS,
            timeout=30,
        )
        frames = endpoint.get_data_frames()

        return {
            "away_team_rotation": frames[0] if len(frames) > 0 else pd.DataFrame(),
            "home_team_rotation": frames[1] if len(frames) > 1 else pd.DataFrame(),
        }

    except Exception as exc:
        print(f"[extract_game_rotation] {game_id} failed: {exc}")
        return {
            "away_team_rotation": pd.DataFrame(),
            "home_team_rotation": pd.DataFrame(),
        }


def _find_officials_dataframe(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """
    不同 nba_api 版本回傳的 DataFrame 順序可能不同。
    所以不用固定第幾個表，而是用欄位名稱判斷哪張像 Officials。
    """
    possible_keywords = {
        "OFFICIAL_ID",
        "OFFICIALID",
        "PERSON_ID",
        "PERSONID",
        "FIRST_NAME",
        "FIRSTNAME",
        "LAST_NAME",
        "LASTNAME",
        "JERSEY_NUM",
        "JERSEYNUM",
    }

    for df in frames:
        if df.empty:
            continue

        upper_cols = {str(col).upper() for col in df.columns}
        matched = upper_cols.intersection(possible_keywords)

        if len(matched) >= 2:
            return df.copy()

    return pd.DataFrame()


def extract_game_officials(game_id: str) -> pd.DataFrame:
    """
    Extract officials for one NBA game.

    Uses direct requests to boxscoresummaryv2 with session warm-up.
    This is more stable than nba_api BoxScoreSummaryV2/V3 in this environment.
    """
    print(f"[extract_game_officials] Fetching officials for game_id={game_id}")

    session = requests.Session()

    try:
        warm_response = session.get(
            NBA_STATS_PAGE_URL,
            headers={
                "User-Agent": NBA_HEADERS["User-Agent"],
                "Accept-Language": NBA_HEADERS["Accept-Language"],
            },
            timeout=(10, 60),
        )
        print(f"[extract_game_officials] Warm-up status: {warm_response.status_code}")

    except Exception as exc:
        raise RuntimeError(f"NBA stats page warm-up failed for game {game_id}: {exc}")

    time.sleep(2)

    try:
        response = session.get(
            BOX_SCORE_SUMMARY_V2_URL,
            headers=NBA_HEADERS,
            params={"GameID": game_id},
            timeout=(10, 180),
        )

        response.raise_for_status()

        data = response.json()
        result_sets = data.get("resultSets", [])

        officials_result = None

        for result in result_sets:
            if result.get("name") == "Officials":
                officials_result = result
                break

        if officials_result is None:
            print(f"[extract_game_officials] No Officials result set for {game_id}")
            return pd.DataFrame()

        columns = officials_result.get("headers", [])
        rows = officials_result.get("rowSet", [])

        if not columns or not rows:
            print(f"[extract_game_officials] Officials empty for {game_id}")
            return pd.DataFrame()

        df = pd.DataFrame(rows, columns=columns)
        df["GAME_ID"] = game_id
        df["SOURCE_ENDPOINT"] = "boxscoresummaryv2_direct"

        print(f"[extract_game_officials] Found {len(df)} officials for {game_id}")

        return df

    except Exception as exc:
        raise RuntimeError(
            f"Failed to extract officials for game {game_id}: "
            f"{type(exc).__name__}: {exc}"
        )


def extract_daily_raw_data(target_date: date) -> dict[str, Any]:
    """
    一天的完整 extract。
    回傳：
    - games_raw：LeagueGameLog 原始資料
    - officials_raw：每場比賽裁判資料
    """
    games_raw = extract_league_games(target_date)

    if games_raw.empty:
        return {
            "target_date": target_date,
            "games_raw": pd.DataFrame(),
            "officials_raw": pd.DataFrame(),
        }

    game_ids = sorted(games_raw["GAME_ID"].dropna().astype(str).unique().tolist())

    official_frames: list[pd.DataFrame] = []

    for game_id in game_ids:
        officials = extract_game_officials(game_id)
        if not officials.empty:
            official_frames.append(officials)

        time.sleep(0.8)

    officials_raw = (
        pd.concat(official_frames, ignore_index=True)
        if official_frames
        else pd.DataFrame()
    )

    return {
        "target_date": target_date,
        "games_raw": games_raw,
        "officials_raw": officials_raw,
    }