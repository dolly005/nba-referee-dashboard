export const teamColors = {
  BOS: '#007A33', BKN: '#111111', NYK: '#F58426', PHI: '#006BB6', TOR: '#CE1141',
  CHI: '#CE1141', CLE: '#860038', DET: '#C8102E', IND: '#FDBB30', MIL: '#00471B',
  ATL: '#E03A3E', CHA: '#1D1160', MIA: '#98002E', ORL: '#0077C0', WAS: '#002B5C',
  DEN: '#0E2240', MIN: '#0C2340', OKC: '#007AC1', POR: '#E03A3E', UTA: '#002B5C',
  GSW: '#1D428A', LAC: '#C8102E', LAL: '#552583', PHX: '#1D1160', SAC: '#5A2D81',
  DAL: '#00538C', HOU: '#CE1141', MEM: '#5D76A9', NOP: '#0C2340', SAS: '#C4CED4'
}

export function groupTeams(teams) {
  return teams.reduce((acc, team) => {
    const conference = team.conference === 'Eastern' ? 'East' : team.conference === 'Western' ? 'West' : team.conference
    const key = `${conference}｜${team.division}`
    if (!acc[key]) acc[key] = []
    acc[key].push(team)
    return acc
  }, {})
}
