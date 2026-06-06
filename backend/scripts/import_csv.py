import argparse
import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()

ARENA_BY_TEAM = {
    'BOS': 'TD Garden', 'BKN': 'Barclays Center', 'NYK': 'Madison Square Garden', 'PHI': 'Wells Fargo Center', 'TOR': 'Scotiabank Arena',
    'CHI': 'United Center', 'CLE': 'Rocket Mortgage FieldHouse', 'DET': 'Little Caesars Arena', 'IND': 'Gainbridge Fieldhouse', 'MIL': 'Fiserv Forum',
    'ATL': 'State Farm Arena', 'CHA': 'Spectrum Center', 'MIA': 'Kaseya Center', 'ORL': 'Kia Center', 'WAS': 'Capital One Arena',
    'DEN': 'Ball Arena', 'MIN': 'Target Center', 'OKC': 'Paycom Center', 'POR': 'Moda Center', 'UTA': 'Delta Center',
    'GSW': 'Chase Center', 'LAC': 'Intuit Dome', 'LAL': 'Crypto.com Arena', 'PHX': 'Footprint Center', 'SAC': 'Golden 1 Center',
    'DAL': 'American Airlines Center', 'HOU': 'Toyota Center', 'MEM': 'FedExForum', 'NOP': 'Smoothie King Center', 'SAS': 'Frost Bank Center',
}


def clean_int(value):
    if pd.isna(value):
        return None
    return int(value)


def clean_text(value, default=None):
    if pd.isna(value):
        return default
    return str(value)


def ensure_column(df, column, default):
    if column not in df.columns:
        df[column] = default
    return df


def normalize_games(games: pd.DataFrame) -> pd.DataFrame:
    games = games.copy()
    games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'], format='mixed', errors='coerce').dt.date

    ensure_column(games, 'SEASON_TYPE', 'Regular Season')
    ensure_column(games, 'POSTSEASON_STAGE', games['SEASON_TYPE'])
    ensure_column(games, 'POSTSEASON_SEASON_TYPE', games['SEASON_TYPE'])
    ensure_column(games, 'NEUTRAL_SITE', 0)
    ensure_column(games, 'SPECIAL_SITE', games['NEUTRAL_SITE'])

    # The database/API uses game_type as the main filter.
    # In the merged file this becomes either Regular Season or Playoffs.
    games['GAME_TYPE'] = games['SEASON_TYPE'].fillna('Regular Season')
    games['SEASON_TYPE'] = games['SEASON_TYPE'].fillna('Regular Season')
    games['POSTSEASON_STAGE'] = games['POSTSEASON_STAGE'].fillna(games['GAME_TYPE'])
    games['POSTSEASON_SEASON_TYPE'] = games['POSTSEASON_SEASON_TYPE'].fillna(games['GAME_TYPE'])
    games['NEUTRAL_SITE'] = games['NEUTRAL_SITE'].fillna(0).astype(int)
    games['SPECIAL_SITE'] = games['SPECIAL_SITE'].fillna(games['NEUTRAL_SITE']).astype(int)

    # Current source files do not include actual arena names.
    # For dashboard grouping, home team arena is used; neutral/special games are flagged by neutral_site/special_site.
    games['ARENA'] = games['HOME_TEAM_ABBREVIATION'].map(ARENA_BY_TEAM)
    return games


def normalize_officials(officials: pd.DataFrame) -> pd.DataFrame:
    officials = officials.copy()
    ensure_column(officials, 'SEASON_TYPE', 'Regular Season')
    ensure_column(officials, 'POSTSEASON_STAGE', officials['SEASON_TYPE'])
    ensure_column(officials, 'POSTSEASON_SEASON_TYPE', officials['SEASON_TYPE'])
    ensure_column(officials, 'SPECIAL_SITE', 0)
    officials['SEASON_TYPE'] = officials['SEASON_TYPE'].fillna('Regular Season')
    officials['POSTSEASON_STAGE'] = officials['POSTSEASON_STAGE'].fillna(officials['SEASON_TYPE'])
    officials['POSTSEASON_SEASON_TYPE'] = officials['POSTSEASON_SEASON_TYPE'].fillna(officials['SEASON_TYPE'])
    officials['SPECIAL_SITE'] = officials['SPECIAL_SITE'].fillna(0).astype(int)
    return officials


def main():
    parser = argparse.ArgumentParser(description='Import NBA regular-season + playoff games and officials CSV files into PostgreSQL.')
    parser.add_argument('--games', required=True, help='Path to nba_games_regular_playoffs_2021_2026.csv')
    parser.add_argument('--officials', required=True, help='Path to nba_game_officials_regular_playoffs_2021_2026.csv')
    args = parser.parse_args()

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL is missing. Copy backend/.env.example to backend/.env first.')

    games = normalize_games(pd.read_csv(Path(args.games)))
    officials = normalize_officials(pd.read_csv(Path(args.officials)))

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            for _, r in games.iterrows():
                cur.execute(
                    '''
                    INSERT INTO games (
                        game_id, game_date, season, game_type, season_type,
                        postseason_stage, postseason_season_type, arena,
                        home_team_id, home_team_abbreviation, home_team_name, home_points,
                        away_team_id, away_team_abbreviation, away_team_name, away_points,
                        home_win, winner_team_id, winner_team_abbreviation,
                        loser_team_id, loser_team_abbreviation, neutral_site, special_site
                    ) VALUES (
                        %(GAME_ID)s, %(GAME_DATE)s, %(SEASON)s, %(GAME_TYPE)s, %(SEASON_TYPE)s,
                        %(POSTSEASON_STAGE)s, %(POSTSEASON_SEASON_TYPE)s, %(ARENA)s,
                        %(HOME_TEAM_ID)s, %(HOME_TEAM_ABBREVIATION)s, %(HOME_TEAM_NAME)s, %(HOME_POINTS)s,
                        %(AWAY_TEAM_ID)s, %(AWAY_TEAM_ABBREVIATION)s, %(AWAY_TEAM_NAME)s, %(AWAY_POINTS)s,
                        %(HOME_WIN)s, %(WINNER_TEAM_ID)s, %(WINNER_TEAM_ABBREVIATION)s,
                        %(LOSER_TEAM_ID)s, %(LOSER_TEAM_ABBREVIATION)s, %(NEUTRAL_SITE)s, %(SPECIAL_SITE)s
                    ) ON CONFLICT (game_id) DO UPDATE SET
                        game_date = EXCLUDED.game_date,
                        season = EXCLUDED.season,
                        game_type = EXCLUDED.game_type,
                        season_type = EXCLUDED.season_type,
                        postseason_stage = EXCLUDED.postseason_stage,
                        postseason_season_type = EXCLUDED.postseason_season_type,
                        arena = EXCLUDED.arena,
                        home_points = EXCLUDED.home_points,
                        away_points = EXCLUDED.away_points,
                        home_win = EXCLUDED.home_win,
                        winner_team_id = EXCLUDED.winner_team_id,
                        winner_team_abbreviation = EXCLUDED.winner_team_abbreviation,
                        loser_team_id = EXCLUDED.loser_team_id,
                        loser_team_abbreviation = EXCLUDED.loser_team_abbreviation,
                        neutral_site = EXCLUDED.neutral_site,
                        special_site = EXCLUDED.special_site
                    ''',
                    r.to_dict(),
                )

            for _, r in officials.iterrows():
                cur.execute(
                    '''
                    INSERT INTO game_officials (
                        game_id, official_id, official_name, first_name, last_name, jersey_num,
                        season_type, postseason_stage, postseason_season_type, special_site
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (game_id, official_id) DO UPDATE SET
                        official_name = EXCLUDED.official_name,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        jersey_num = EXCLUDED.jersey_num,
                        season_type = EXCLUDED.season_type,
                        postseason_stage = EXCLUDED.postseason_stage,
                        postseason_season_type = EXCLUDED.postseason_season_type,
                        special_site = EXCLUDED.special_site
                    ''',
                    (
                        clean_int(r['GAME_ID']),
                        clean_int(r['OFFICIAL_ID']),
                        clean_text(r.get('OFFICIAL_NAME')),
                        clean_text(r.get('FIRST_NAME')),
                        clean_text(r.get('LAST_NAME')),
                        clean_int(r.get('JERSEY_NUM')),
                        clean_text(r.get('SEASON_TYPE'), 'Regular Season'),
                        clean_text(r.get('POSTSEASON_STAGE'), 'Regular Season'),
                        clean_text(r.get('POSTSEASON_SEASON_TYPE'), 'Regular Season'),
                        clean_int(r.get('SPECIAL_SITE')) or 0,
                    ),
                )
        conn.commit()

    print(f'Imported {len(games)} games and {len(officials)} official-game rows.')
    print('Game types imported:', ', '.join(sorted(games['GAME_TYPE'].dropna().unique())))


if __name__ == '__main__':
    main()
