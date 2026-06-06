from __future__ import annotations

import time
from datetime import date
from typing import Any

import pandas as pd
from nba_api.stats.endpoints import leaguegamelog, gamerotation

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
    "x-nba-stats-token": "true",
    "User-Agent": "Mozilla/5.0",
    "x-nba-stats-origin": "stats",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
}


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


def extract_league_games(target_date: date) -> pd.DataFrame:
    """
    抓指定日期的例行賽 + 季後賽比賽。

    修正版：
    不直接把 date_from / date_to 丟給 nba_api，
    而是先抓整季，再用 pandas 篩選日期。
    這樣比較穩，避免 NBA API 日期參數偶爾抓不到資料。
    """
    season = get_nba_season(target_date)

    all_frames: list[pd.DataFrame] = []

    for season_type in ["Regular Season", "Playoffs"]:
        try:
            endpoint = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star=season_type,
                player_or_team_abbreviation="T",
                headers=NBA_HEADERS,
                timeout=30,
            )

            frames = endpoint.get_data_frames()

            if frames and not frames[0].empty:
                df = frames[0].copy()

                # 統一日期格式
                df["GAME_DATE_PARSED"] = pd.to_datetime(
                    df["GAME_DATE"],
                    errors="coerce"
                ).dt.date

                # 只保留指定日期
                df = df[df["GAME_DATE_PARSED"] == target_date].copy()

                if not df.empty:
                    df["SEASON_TYPE"] = season_type
                    df["NBA_SEASON"] = season
                    all_frames.append(df)

            time.sleep(0.8)

        except Exception as exc:
            print(f"[extract_league_games] {season_type} failed: {exc}")

    if not all_frames:
        print(f"[extract_league_games] No games found for {target_date}, season={season}")
        return pd.DataFrame()

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
    優先用 BoxScoreSummaryV3。
    如果 V3 無法使用，就 fallback 到 V2。
    """
    frames: list[pd.DataFrame] = []

    if boxscoresummaryv3 is not None:
        try:
            endpoint = boxscoresummaryv3.BoxScoreSummaryV3(
                game_id=game_id,
                headers=NBA_HEADERS,
                timeout=30,
            )
            frames = endpoint.get_data_frames()
            officials = _find_officials_dataframe(frames)
            if not officials.empty:
                officials["GAME_ID"] = game_id
                officials["SOURCE_ENDPOINT"] = "BoxScoreSummaryV3"
                return officials

            time.sleep(0.8)

        except Exception as exc:
            print(f"[extract_game_officials] V3 failed for {game_id}: {exc}")

    try:
        endpoint = boxscoresummaryv2.BoxScoreSummaryV2(
            game_id=game_id,
            headers=NBA_HEADERS,
            timeout=30,
        )
        frames = endpoint.get_data_frames()
        officials = _find_officials_dataframe(frames)
        if not officials.empty:
            officials["GAME_ID"] = game_id
            officials["SOURCE_ENDPOINT"] = "BoxScoreSummaryV2"
            return officials

    except Exception as exc:
        print(f"[extract_game_officials] V2 failed for {game_id}: {exc}")

    return pd.DataFrame()


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