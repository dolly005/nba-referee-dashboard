CREATE TABLE IF NOT EXISTS update_logs (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    target_date DATE,
    source TEXT NOT NULL DEFAULT 'nba_api',
    status TEXT NOT NULL DEFAULT 'running',
    games_count INTEGER NOT NULL DEFAULT 0,
    referees_count INTEGER NOT NULL DEFAULT 0,
    game_referees_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_games_game_id
ON games (game_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_game_officials_game_official
ON game_officials (game_id, official_id);