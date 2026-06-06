import { useMemo, useState } from 'react'
import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { apiGet } from '../api/client'
import Filters from '../components/Filters'
import Skeleton from '../components/Skeleton'
import TeamLogo from '../components/TeamLogo'
import { teamColors } from '../data/teamMeta'
import { useFetch } from '../hooks'

const VENUES = [
  { value: 'all', label: '所有場次' },
  { value: 'home', label: '僅主場' },
  { value: 'away', label: '僅客場' },
]

const CONFERENCES = [
  { value: 'all', label: '全聯盟' },
  { value: 'East', label: '東區' },
  { value: 'West', label: '西區' },
]

function winRatePct(value) {
  return Math.round(Number(value || 0) * 100)
}

function rankColor(row) {
  if (teamColors[row.team]) return teamColors[row.team]
  return row.conference === 'East' ? '#2563eb' : '#dc2626'
}

function TeamTick({ x, y, payload }) {
  const abbr = payload.value
  return (
    <foreignObject x={x - 112} y={y - 14} width="108" height="28">
      <div className="flex items-center justify-end gap-2 pr-1 text-xs text-white">
        <span>{abbr}</span>
      </div>
    </foreignObject>
  )
}

function CustomTooltip({ active, payload, title }) {
  if (!active || !payload || payload.length === 0) return null

  const row = payload[0].payload

  return (
    <div className="rounded-2xl border border-white/10 bg-[#0f1b2d] px-4 py-3 shadow-glow">
      <p className="text-sm font-black text-white">
        第 {row.chartRank ?? '-'} 名｜{row.full_name || row.team}
      </p>
      <p className="mt-1 text-sm font-bold text-white">
        {title}
      </p>
      <p className="mt-1 text-sm text-slate-200">
        {row.chartLabel}
      </p>
      <p className="mt-1 text-xs text-slate-400">
        {row.conference}｜{row.wins ?? 0}W-{row.losses ?? 0}L
      </p>
    </div>
  )
}

function RankingChart({
  title,
  data,
  metric,
  rankKey,
  domain,
  formatter,
  sortDirection = 'desc',
  record = false,
}) {
  const sorted = useMemo(() => {
    const rows = [...data].filter((row) => row[metric] !== null && row[metric] !== undefined)

    rows.sort((a, b) => {
      if (rankKey && a[rankKey] !== undefined && b[rankKey] !== undefined) {
        return Number(a[rankKey]) - Number(b[rankKey])
      }

      return sortDirection === 'asc'
        ? Number(a[metric]) - Number(b[metric])
        : Number(b[metric]) - Number(a[metric])
    })

   return rows.map((row) => {
      const valueLabel = record
        ? `${winRatePct(row[metric])}% ${row.wins}-${row.losses}`
        : formatter(row[metric])

      const rank = rankKey ? row[rankKey] : null

      return {
        ...row,
        chartValue: metric === 'win_rate' ? winRatePct(row[metric]) : Number(row[metric]),
        chartLabel: rank ? `第 ${rank} 名｜${valueLabel}` : valueLabel,
        chartRank: rank,
      }
    })
  }, [data, metric, rankKey, sortDirection, formatter, record])

  const height = Math.max(420, sorted.length * 34 + 80)

  return (
    <section className="rounded-3xl border border-white/10 bg-panel p-5 shadow-glow">
      <h2 className="mb-4 text-xl font-black text-white">{title}</h2>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={sorted} layout="vertical" margin={{ top: 8, right: 92, bottom: 8, left: 36 }}>
            <XAxis type="number" domain={domain} tick={{ fill: '#cbd5e1' }} axisLine={{ stroke: '#334155' }} tickLine={{ stroke: '#334155' }} />
            <YAxis type="category" dataKey="team" width={78} tick={<TeamTick />} axisLine={{ stroke: '#334155' }} tickLine={false} />
            <Tooltip
              cursor={{ fill: 'rgba(255,255,255,0.06)' }}
              content={<CustomTooltip title={title} />}
            />
            <Bar dataKey="chartValue" isAnimationActive radius={[0, 12, 12, 0]}>
              {sorted.map((row) => <Cell key={row.team} fill={rankColor(row)} />)}
              <LabelList
                dataKey="chartLabel"
                position="right"
                fill="#fff"
                fontSize={12}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}

export default function LeagueRankingsPage({ seasons, gameTypes, postseasonStages }) {
  const [season, setSeason] = useState('2021-22')
  const [gameType, setGameType] = useState('Regular Season')
  const [postseasonStage, setPostseasonStage] = useState('全部階段')
  const [venue, setVenue] = useState('all')
  const [conference, setConference] = useState('all')
  const { data, loading, error } = useFetch(
    () => apiGet('/api/league-rankings', { season, game_type: gameType, postseason_stage: postseasonStage, venue, conference }),
    [season, gameType, postseasonStage, venue, conference]
  )
  const teams = data?.teams || []

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
        <div className="mb-4">
          <h1 className="text-2xl font-black text-white">聯盟排名</h1>
          <p className="text-sm text-slate-400">依賽季、賽事類別、主客場範圍與東西區篩選球隊排名。</p>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <label className="text-sm text-slate-300">
            場次範圍
            <select value={venue} onChange={(e) => setVenue(e.target.value)} className="mt-1 w-full rounded-2xl border border-white/10 bg-navy px-4 py-3 text-white outline-none focus:border-nbaRed">
              {VENUES.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
            </select>
          </label>
          <label className="text-sm text-slate-300">
            範圍
            <select value={conference} onChange={(e) => setConference(e.target.value)} className="mt-1 w-full rounded-2xl border border-white/10 bg-navy px-4 py-3 text-white outline-none focus:border-nbaRed">
              {CONFERENCES.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
            </select>
          </label>
        </div>
      </section>
      {loading ? <Skeleton rows={10} /> : error ? <p className="text-nbaRed">{error.message}</p> : (
        <>
          <section className="grid grid-cols-2 gap-3 rounded-3xl border border-white/10 bg-panel/80 p-4 shadow-glow md:grid-cols-6">
            {teams.map((team) => (
              <div key={team.team} className="flex items-center justify-center rounded-2xl bg-white/[0.03] p-2" title={team.full_name}>
                <TeamLogo abbr={team.team} size="sm" />
              </div>
            ))}
          </section>
          <RankingChart
            title="① 球隊勝率排名"
            data={teams}
            metric="win_rate"
            rankKey="win_rate_rank"
            domain={[0, 100]}
            formatter={(v) => `${winRatePct(v)}%`}
            record
          />

          <RankingChart
            title="② 場均得分排名"
            data={teams}
            metric="ppg"
            rankKey="ppg_rank"
            domain={['dataMin - 3', 'dataMax + 3']}
            formatter={(v) => Number(v || 0).toFixed(1)}
          />

          <RankingChart
            title="③ 場均失分排名"
            data={teams}
            metric="opp_ppg"
            rankKey="opp_ppg_rank"
            domain={['dataMin - 3', 'dataMax + 3']}
            formatter={(v) => Number(v || 0).toFixed(1)}
            sortDirection="asc"
          />
        </>
      )}
    </div>
  )
}
