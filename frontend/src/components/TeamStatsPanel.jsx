import MetricBox from './MetricBox'

export default function TeamStatsPanel({ stats }) {
  if (!stats || Array.isArray(stats)) return null
  return (
    <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-panel2 to-panel p-6 shadow-glow">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm text-slate-400">場均數據面板</p>
          <h3 className="text-xl font-black text-white">{stats.team}｜{stats.conference} 分區</h3>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <MetricBox
          label="場均得分 PPG"
          value={stats.ppg}
          diff={Number(stats.ppg || 0) - Number(stats.league_avg_ppg || 0)}
          leagueRank={stats.ppg_rank_league}
          conferenceRank={stats.ppg_rank_conference}
        />
        <MetricBox
          label="場均失分 Opp PPG"
          value={stats.opp_ppg}
          diff={Number(stats.opp_ppg || 0) - Number(stats.league_avg_opp_ppg || 0)}
          leagueRank={stats.opp_ppg_rank_league}
          conferenceRank={stats.opp_ppg_rank_conference}
          lowerIsBetter
        />
      </div>
    </div>
  )
}
