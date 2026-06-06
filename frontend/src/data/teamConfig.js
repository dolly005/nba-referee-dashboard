export const teams = [
  { abbr: 'BOS', fullName: 'Boston Celtics', teamId: '1610612738', conference: 'East', division: 'Atlantic' },
  { abbr: 'BKN', fullName: 'Brooklyn Nets', teamId: '1610612751', conference: 'East', division: 'Atlantic' },
  { abbr: 'NYK', fullName: 'New York Knicks', teamId: '1610612752', conference: 'East', division: 'Atlantic' },
  { abbr: 'PHI', fullName: 'Philadelphia 76ers', teamId: '1610612755', conference: 'East', division: 'Atlantic' },
  { abbr: 'TOR', fullName: 'Toronto Raptors', teamId: '1610612761', conference: 'East', division: 'Atlantic' },
  { abbr: 'CHI', fullName: 'Chicago Bulls', teamId: '1610612741', conference: 'East', division: 'Central' },
  { abbr: 'CLE', fullName: 'Cleveland Cavaliers', teamId: '1610612739', conference: 'East', division: 'Central' },
  { abbr: 'DET', fullName: 'Detroit Pistons', teamId: '1610612765', conference: 'East', division: 'Central' },
  { abbr: 'IND', fullName: 'Indiana Pacers', teamId: '1610612754', conference: 'East', division: 'Central' },
  { abbr: 'MIL', fullName: 'Milwaukee Bucks', teamId: '1610612749', conference: 'East', division: 'Central' },
  { abbr: 'ATL', fullName: 'Atlanta Hawks', teamId: '1610612737', conference: 'East', division: 'Southeast' },
  { abbr: 'CHA', fullName: 'Charlotte Hornets', teamId: '1610612766', conference: 'East', division: 'Southeast' },
  { abbr: 'MIA', fullName: 'Miami Heat', teamId: '1610612748', conference: 'East', division: 'Southeast' },
  { abbr: 'ORL', fullName: 'Orlando Magic', teamId: '1610612753', conference: 'East', division: 'Southeast' },
  { abbr: 'WAS', fullName: 'Washington Wizards', teamId: '1610612764', conference: 'East', division: 'Southeast' },
  { abbr: 'DEN', fullName: 'Denver Nuggets', teamId: '1610612743', conference: 'West', division: 'Northwest' },
  { abbr: 'MIN', fullName: 'Minnesota Timberwolves', teamId: '1610612750', conference: 'West', division: 'Northwest' },
  { abbr: 'OKC', fullName: 'Oklahoma City Thunder', teamId: '1610612760', conference: 'West', division: 'Northwest' },
  { abbr: 'POR', fullName: 'Portland Trail Blazers', teamId: '1610612757', conference: 'West', division: 'Northwest' },
  { abbr: 'UTA', fullName: 'Utah Jazz', teamId: '1610612762', conference: 'West', division: 'Northwest' },
  { abbr: 'GSW', fullName: 'Golden State Warriors', teamId: '1610612744', conference: 'West', division: 'Pacific' },
  { abbr: 'LAC', fullName: 'LA Clippers', teamId: '1610612746', conference: 'West', division: 'Pacific' },
  { abbr: 'LAL', fullName: 'Los Angeles Lakers', teamId: '1610612747', conference: 'West', division: 'Pacific' },
  { abbr: 'PHX', fullName: 'Phoenix Suns', teamId: '1610612756', conference: 'West', division: 'Pacific' },
  { abbr: 'SAC', fullName: 'Sacramento Kings', teamId: '1610612758', conference: 'West', division: 'Pacific' },
  { abbr: 'DAL', fullName: 'Dallas Mavericks', teamId: '1610612742', conference: 'West', division: 'Southwest' },
  { abbr: 'HOU', fullName: 'Houston Rockets', teamId: '1610612745', conference: 'West', division: 'Southwest' },
  { abbr: 'MEM', fullName: 'Memphis Grizzlies', teamId: '1610612763', conference: 'West', division: 'Southwest' },
  { abbr: 'NOP', fullName: 'New Orleans Pelicans', teamId: '1610612740', conference: 'West', division: 'Southwest' },
  { abbr: 'SAS', fullName: 'San Antonio Spurs', teamId: '1610612759', conference: 'West', division: 'Southwest' },
]

export const teamByAbbr = Object.fromEntries(teams.map((team) => [team.abbr, team]))

export function logoUrl(abbr) {
  const team = teamByAbbr[abbr]
  return team ? `https://cdn.nba.com/logos/nba/${team.teamId}/global/L/logo.svg` : ''
}

export function displayConference(conference) {
  if (conference === 'Eastern') return 'East'
  if (conference === 'Western') return 'West'
  return conference
}
