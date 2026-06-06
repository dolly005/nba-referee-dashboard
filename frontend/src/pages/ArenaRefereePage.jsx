import { useMemo, useState } from 'react'
import { apiGet } from '../api/client'
import ArenaStatsPanel from '../components/ArenaStatsPanel'
import Filters from '../components/Filters'
import RateCell from '../components/RateCell'
import Skeleton from '../components/Skeleton'
import SortableTable from '../components/SortableTable'
import TeamLogo from '../components/TeamLogo'
import { useFetch } from '../hooks'

export default function ArenaRefereePage({ seasons, gameTypes, postseasonStages, arenas }) {
  const [season, setSeason] = useState('2021-22')
  const [gameType, setGameType] = useState('Regular Season')
  const [postseasonStage, setPostseasonStage] = useState('全部階段')
  const [arena, setArena] = useState('TD Garden')
  const query = { arena, season, game_type: gameType, postseason_stage: postseasonStage }
  const { data, loading, error } = useFetch(() => apiGet('/api/arena-referee', query), [arena, season, gameType, postseasonStage])
  const statsState = useFetch(() => apiGet('/api/arena-stats', query), [arena, season, gameType, postseasonStage])
  const selectedArena = arenas.find((a) => a.arena_name === arena)

  const columns = useMemo(() => [
    { key: 'official_name', label: '裁判姓名' },
    { key: 'games', label: '場數' },
    { key: 'home_wins', label: '主隊勝' },
    { key: 'home_losses', label: '主隊敗' },
    { key: 'home_win_rate', label: '主隊勝率（W-L）', render: (row) => <RateCell rate={row.home_win_rate} wins={row.home_wins} losses={row.home_losses} /> },
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
      {statsState.loading ? <Skeleton rows={3} /> : !statsState.error && <ArenaStatsPanel stats={statsState.data} />}
      <section className="rounded-3xl border border-white/10 bg-panel p-5 shadow-glow">
        <div className="mb-4 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 className="text-xl font-black">場館選擇器</h2>
            <p className="text-sm text-slate-400">目前：{selectedArena?.arena_name_zh}｜{selectedArena?.team_abbreviation} {selectedArena?.team_name}</p>
          </div>
          <select value={arena} onChange={(e) => setArena(e.target.value)} className="rounded-2xl border border-white/10 bg-navy px-4 py-3 text-white outline-none focus:border-nbaRed">
            {arenas.map((a) => (
              <option key={a.arena_name} value={a.arena_name}>{a.arena_name}｜{a.team_abbreviation}</option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {arenas.map((a) => (
            <button key={a.arena_name} type="button" onClick={() => setArena(a.arena_name)} className={`rounded-2xl border p-4 text-left transition ${arena === a.arena_name ? 'border-nbaRed bg-nbaRed/20' : 'border-white/10 bg-white/5 hover:bg-white/10'}`}>
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="font-bold text-white">{a.arena_name}</p>
                  <p className="text-sm text-slate-400">{a.arena_name_zh}</p>
                </div>
                <TeamLogo abbr={a.team_abbreviation} size="md" />
              </div>
            </button>
          ))}
        </div>
      </section>
      {loading ? <Skeleton /> : error ? <p className="text-nbaRed">{error.message}</p> : <SortableTable rows={data} columns={columns} defaultSortKey="games" />}
    </div>
  )
}
