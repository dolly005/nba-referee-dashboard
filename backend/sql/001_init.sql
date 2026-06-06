DROP TABLE IF EXISTS game_officials;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS arenas;
DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    abbreviation VARCHAR(3) PRIMARY KEY,
    full_name TEXT NOT NULL,
    conference TEXT NOT NULL,
    division TEXT NOT NULL
);

CREATE TABLE arenas (
    arena_name TEXT PRIMARY KEY,
    arena_name_zh TEXT NOT NULL,
    team_abbreviation VARCHAR(3) NOT NULL REFERENCES teams(abbreviation)
);

CREATE TABLE games (
    game_id BIGINT PRIMARY KEY,
    game_date DATE NOT NULL,
    season VARCHAR(7) NOT NULL,
    game_type TEXT NOT NULL DEFAULT 'Regular Season',
    season_type TEXT NOT NULL DEFAULT 'Regular Season',
    postseason_stage TEXT NOT NULL DEFAULT 'Regular Season',
    postseason_season_type TEXT NOT NULL DEFAULT 'Regular Season',
    arena TEXT REFERENCES arenas(arena_name),
    home_team_id BIGINT NOT NULL,
    home_team_abbreviation VARCHAR(3) NOT NULL REFERENCES teams(abbreviation),
    home_team_name TEXT NOT NULL,
    home_points INT NOT NULL,
    away_team_id BIGINT NOT NULL,
    away_team_abbreviation VARCHAR(3) NOT NULL REFERENCES teams(abbreviation),
    away_team_name TEXT NOT NULL,
    away_points INT NOT NULL,
    home_win INT NOT NULL CHECK (home_win IN (0, 1)),
    winner_team_id BIGINT NOT NULL,
    winner_team_abbreviation VARCHAR(3) NOT NULL REFERENCES teams(abbreviation),
    loser_team_id BIGINT NOT NULL,
    loser_team_abbreviation VARCHAR(3) NOT NULL REFERENCES teams(abbreviation),
    neutral_site INT NOT NULL DEFAULT 0 CHECK (neutral_site IN (0, 1)),
    special_site INT NOT NULL DEFAULT 0 CHECK (special_site IN (0, 1))
);

CREATE TABLE game_officials (
    id BIGSERIAL PRIMARY KEY,
    game_id BIGINT NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    official_id BIGINT NOT NULL,
    official_name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    jersey_num INT,
    season_type TEXT NOT NULL DEFAULT 'Regular Season',
    postseason_stage TEXT NOT NULL DEFAULT 'Regular Season',
    postseason_season_type TEXT NOT NULL DEFAULT 'Regular Season',
    special_site INT NOT NULL DEFAULT 0 CHECK (special_site IN (0, 1)),
    UNIQUE (game_id, official_id)
);

CREATE INDEX idx_games_season_type ON games(season, game_type);
CREATE INDEX idx_games_season ON games(season);
CREATE INDEX idx_games_game_type ON games(game_type);
CREATE INDEX idx_games_postseason_stage ON games(postseason_stage);
CREATE INDEX idx_games_home_team ON games(home_team_abbreviation);
CREATE INDEX idx_games_away_team ON games(away_team_abbreviation);
CREATE INDEX idx_games_arena ON games(arena);
CREATE INDEX idx_officials_game_id ON game_officials(game_id);
CREATE INDEX idx_officials_official_id ON game_officials(official_id);

INSERT INTO teams (abbreviation, full_name, conference, division) VALUES
('BOS','Boston Celtics','Eastern','Atlantic'),
('BKN','Brooklyn Nets','Eastern','Atlantic'),
('NYK','New York Knicks','Eastern','Atlantic'),
('PHI','Philadelphia 76ers','Eastern','Atlantic'),
('TOR','Toronto Raptors','Eastern','Atlantic'),
('CHI','Chicago Bulls','Eastern','Central'),
('CLE','Cleveland Cavaliers','Eastern','Central'),
('DET','Detroit Pistons','Eastern','Central'),
('IND','Indiana Pacers','Eastern','Central'),
('MIL','Milwaukee Bucks','Eastern','Central'),
('ATL','Atlanta Hawks','Eastern','Southeast'),
('CHA','Charlotte Hornets','Eastern','Southeast'),
('MIA','Miami Heat','Eastern','Southeast'),
('ORL','Orlando Magic','Eastern','Southeast'),
('WAS','Washington Wizards','Eastern','Southeast'),
('DEN','Denver Nuggets','Western','Northwest'),
('MIN','Minnesota Timberwolves','Western','Northwest'),
('OKC','Oklahoma City Thunder','Western','Northwest'),
('POR','Portland Trail Blazers','Western','Northwest'),
('UTA','Utah Jazz','Western','Northwest'),
('GSW','Golden State Warriors','Western','Pacific'),
('LAC','LA Clippers','Western','Pacific'),
('LAL','Los Angeles Lakers','Western','Pacific'),
('PHX','Phoenix Suns','Western','Pacific'),
('SAC','Sacramento Kings','Western','Pacific'),
('DAL','Dallas Mavericks','Western','Southwest'),
('HOU','Houston Rockets','Western','Southwest'),
('MEM','Memphis Grizzlies','Western','Southwest'),
('NOP','New Orleans Pelicans','Western','Southwest'),
('SAS','San Antonio Spurs','Western','Southwest');

INSERT INTO arenas (arena_name, arena_name_zh, team_abbreviation) VALUES
('TD Garden','TD花園','BOS'),
('Barclays Center','巴克萊中心','BKN'),
('Madison Square Garden','麥迪遜廣場花園','NYK'),
('Wells Fargo Center','富國銀行中心','PHI'),
('Scotiabank Arena','豐業銀行體育館','TOR'),
('United Center','聯合中心','CHI'),
('Rocket Mortgage FieldHouse','火箭信貸球館','CLE'),
('Little Caesars Arena','小凱薩體育館','DET'),
('Gainbridge Fieldhouse','蓋營球館','IND'),
('Fiserv Forum','第一服務廣場','MIL'),
('State Farm Arena','州立農業球館','ATL'),
('Spectrum Center','光譜中心','CHA'),
('Kaseya Center','卡賽亞中心','MIA'),
('Kia Center','起亞中心','ORL'),
('Capital One Arena','第一資本體育館','WAS'),
('Ball Arena','波爾體育館','DEN'),
('Target Center','標靶中心','MIN'),
('Paycom Center','Paycom中心','OKC'),
('Moda Center','摩達中心','POR'),
('Delta Center','三角洲中心','UTA'),
('Chase Center','大通銀行中心','GSW'),
('Intuit Dome','直覺巨蛋','LAC'),
('Crypto.com Arena','加密貨幣網體育館','LAL'),
('Footprint Center','足跡中心','PHX'),
('Golden 1 Center','黃金一號中心','SAC'),
('American Airlines Center','美國航空中心','DAL'),
('Toyota Center','豐田中心','HOU'),
('FedExForum','聯邦快遞廣場','MEM'),
('Smoothie King Center','冰沙國王中心','NOP'),
('Frost Bank Center','冰霜銀行中心','SAS');
