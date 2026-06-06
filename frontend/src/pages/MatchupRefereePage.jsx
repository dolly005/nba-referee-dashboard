import { useMemo, useState } from 'react'
import { apiGet } from '../api/client'
import Filters from '../components/Filters'
import RateCell from '../components/RateCell'
import Skeleton from '../components/Skeleton'
import SortableTable from '../components/SortableTable'
import TeamGrid from '../components/TeamGrid'
import TeamLogo from '../components/TeamLogo'
import { useFetch } from '../hooks'

export default function MatchupRefereePage({ seasons, gameTypes, postseasonStages, teams }) {
  const [season, setSeason] = useState('2021-22')
  const [gameType, setGameType] = useState('Regular Season')
  const [postseasonStage, setPostseasonStage] = useState('全部階段')
  const [teamA, setTeamA] = useState('BOS')
  const [teamB, setTeamB] = useState('LAL')
  const { data, loading, error } = useFetch(
    () => apiGet('/api/matchup-referee', { team_a: teamA, team_b: teamB, season, game_type: gameType, postseason_stage: postseasonStage }),
    [teamA, teamB, season, gameType, postseasonStage]
  )

  function changeTeamA(next) {
    setTeamA(next)
    if (next === teamB) setTeamB(teams.find((t) => t.abbreviation !== next)?.abbreviation || 'LAL')
  }

  const columns = useMemo(() => [
    { key: 'official_name', label: '裁判姓名' },
    { key: 'games', label: '場數' },
    { key: 'wins', label: `${teamA} 勝` },
    { key: 'losses', label: `${teamA} 敗` },
    { key: 'win_rate', label: `${teamA} 勝率（W-L）`, render: (row) => <RateCell rate={row.win_rate} wins={row.wins} losses={row.losses} /> },
  ], [teamA])

  return (
    <div className="space-y-6">
      <Filters
        season={season}
        setSeason={setSeason}
        gameType={gameType}
        setGameType={setGameType}
        seasons={seasons}
        gameTypes={gameTypes}
        postseasonStage={postseasonStage}
        setPostseasonStage={setPostseasonStage}
        postseasonStages={postseasonStages}
      />
      <section className="rounded-3xl border border-white/10 bg-panel p-5 shadow-glow">
        <h2 className="mb-4 flex items-center gap-3 text-xl font-black">球隊 A 選擇器：<TeamLogo abbr={teamA} /></h2>
        <TeamGrid teams={teams} selected={teamA} onSelect={changeTeamA} />
      </section>
      <section className="rounded-3xl border border-white/10 bg-panel p-5 shadow-glow">
        <h2 className="mb-4 flex items-center gap-3 text-xl font-black">球隊 B 選擇器：<TeamLogo abbr={teamB} /></h2>
        <TeamGrid teams={teams} selected={teamB} onSelect={setTeamB} disabledTeam={teamA} />
      </section>
      {loading ? <Skeleton /> : error ? <p className="text-nbaRed">{error.message}</p> : <SortableTable rows={data} columns={columns} defaultSortKey="games" />}
    </div>
  )
}
