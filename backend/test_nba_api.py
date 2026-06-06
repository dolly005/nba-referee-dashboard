from datetime import date
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

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

target_date = date(2024, 1, 15)

print("Testing NBA API...")
print("Target date:", target_date)

try:
    endpoint = leaguegamelog.LeagueGameLog(
    season="2023-24",
    season_type_all_star="Regular Season",
    player_or_team_abbreviation="T",
    date_from_nullable="01/15/2024",
    date_to_nullable="01/15/2024",
    headers=NBA_HEADERS,
    timeout=120,
)

    frames = endpoint.get_data_frames()

    print("Number of dataframes:", len(frames))

    if not frames:
        print("No dataframe returned.")
        raise SystemExit

    df = frames[0]

    print("Raw shape:", df.shape)
    print("Columns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    if "GAME_DATE" not in df.columns:
        print("GAME_DATE column not found.")
        raise SystemExit

    df["GAME_DATE_PARSED"] = pd.to_datetime(
        df["GAME_DATE"],
        errors="coerce"
    ).dt.date

    print("\nDate range:")
    print(df["GAME_DATE_PARSED"].min(), "to", df["GAME_DATE_PARSED"].max())

    filtered = df[df["GAME_DATE_PARSED"] == target_date]

    print("\nFiltered shape for 2024-01-15:")
    print(filtered.shape)

    print("\nFiltered rows:")
    print(filtered[["GAME_ID", "GAME_DATE", "MATCHUP", "TEAM_ABBREVIATION", "PTS"]].head(30))

except Exception as e:
    print("ERROR:")
    print(type(e))
    print(e)