import { useMemo, useState } from 'react'
import { apiGet } from '../api/client'
import Filters from '../components/Filters'
import Skeleton from '../components/Skeleton'
import SortableTable from '../components/SortableTable'
import SummaryBanner from '../components/SummaryBanner'
import { useFetch } from '../hooks'

export default function RefereesPage({ seasons, gameTypes, postseasonStages }) {
  const [season, setSeason] = useState('2021-22')
  const [gameType, setGameType] = useState('Regular Season')
  const [postseasonStage, setPostseasonStage] = useState('全部階段')
  const [search, setSearch] = useState('')
  const query = { season, game_type: gameType, postseason_stage: postseasonStage }
  const { data, loading, error } = useFetch(() => apiGet('/api/referees', { ...query, search }), [season, gameType, postseasonStage, search])
  const summaryState = useFetch(() => apiGet('/api/referees/summary', query), [season, gameType, postseasonStage])

  const columns = useMemo(() => [
    { key: 'official_name', label: '裁判姓名', render: (row) => <button className="font-bold text-white underline-offset-4 hover:underline">{row.official_name}</button> },
    { key: 'games', label: '吹判場次' },
    { key: 'home_win_rate', label: '主場勝率', render: (row) => <strong>{Math.round(row.home_win_rate || 0)}%</strong> },
    { key: 'away_win_rate', label: '客場勝率', render: (row) => <strong>{Math.round(row.away_win_rate || 0)}%</strong> },
  ], [])

  return (
    <div>
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
      {summaryState.loading ? <Skeleton rows={2} /> : !summaryState.error && <SummaryBanner summary={summaryState.data} />}
      <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-black">裁判名單</h2>
          <p className="text-sm text-slate-400">依目前賽季、賽事類別與季後賽階段彙總裁判執法場次、主場勝率與客場勝率。</p>
        </div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="搜尋裁判姓名..."
          className="w-full rounded-2xl border border-white/10 bg-panel px-4 py-3 text-white outline-none focus:border-nbaRed md:w-72"
        />
      </div>
      {loading ? <Skeleton /> : error ? <p className="text-nbaRed">{error.message}</p> : <SortableTable rows={data} columns={columns} defaultSortKey="games" />}
    </div>
  )
}
