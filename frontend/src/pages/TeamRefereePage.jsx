import { useMemo, useState } from 'react'
import { apiGet } from '../api/client'
import Filters from '../components/Filters'
import RateCell from '../components/RateCell'
import Skeleton from '../components/Skeleton'
import SortableTable from '../components/SortableTable'
import StatCard from '../components/StatCard'
import TeamGrid from '../components/TeamGrid'
import TeamLogo from '../components/TeamLogo'
import TeamStatsPanel from '../components/TeamStatsPanel'
import { useFetch } from '../hooks'

export default function TeamRefereePage({ seasons, gameTypes, postseasonStages, teams }) {
  const [season, setSeason] = useState('2021-22')
  const [gameType, setGameType] = useState('Regular Season')
  const [postseasonStage, setPostseasonStage] = useState('全部階段')
  const [team, setTeam] = useState('BOS')
  const query = { team, season, game_type: gameType, postseason_stage: postseasonStage }
  const { data, loading, error } = useFetch(() => apiGet('/api/team-referee', query), [team, season, gameType, postseasonStage])
  const statsState = useFetch(() => apiGet('/api/team-stats', query), [team, season, gameType, postseasonStage])

  const teamSummary = data[0] || {}
  const columns = useMemo(() => [
    { key: 'official_name', label: '裁判姓名' },
    { key: 'games', label: '場數' },
    { key: 'wins', label: '勝' },
    { key: 'losses', label: '敗' },
    { key: 'win_rate', label: '勝率（W-L）', render: (row) => <RateCell rate={row.win_rate} wins={row.wins} losses={row.losses} /> },
  ], [])

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
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-[0.9fr_1.4fr]">
        <StatCard title={<span className="inline-flex items-center gap-2"><TeamLogo abbr={team} size="sm" />本賽季勝率</span>} value={teamSummary.team_win_rate ?? 0} subtitle={`${teamSummary.team_wins ?? 0}W-${teamSummary.team_losses ?? 0}L，共 ${teamSummary.team_games ?? 0} 場`} />
        {statsState.loading ? <Skeleton rows={3} /> : !statsState.error && <TeamStatsPanel stats={statsState.data} />}
      </section>
      <section className="rounded-3xl border border-white/10 bg-panel p-5 shadow-glow">
        <h2 className="mb-4 text-xl font-black">球隊選擇器</h2>
        <TeamGrid teams={teams} selected={team} onSelect={setTeam} />
      </section>
      {loading ? <Skeleton /> : error ? <p className="text-nbaRed">{error.message}</p> : <SortableTable rows={data} columns={columns} defaultSortKey="games" />}
    </div>
  )
}
