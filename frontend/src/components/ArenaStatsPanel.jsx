import MetricBox from './MetricBox'
import StatCard from './StatCard'

export default function ArenaStatsPanel({ stats }) {
  if (!stats || Array.isArray(stats)) return null
  return (
    <section className="grid grid-cols-1 gap-4 lg:grid-cols-[0.9fr_1.4fr]">
      <StatCard
        title={`${stats.arena} 主場勝率`}
        value={Number(stats.home_win_rate || 0) * 100}
        subtitle={`${stats.home_team}｜${stats.home_wins ?? 0}W-${stats.home_losses ?? 0}L，共 ${stats.games ?? 0} 場`}
      />
      <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-panel2 to-panel p-6 shadow-glow">
        <div className="mb-4">
          <p className="text-sm text-slate-400">主場數據面板</p>
          <h3 className="text-xl font-black text-white">{stats.home_team}｜{stats.conference} 分區</h3>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <MetricBox
            label="主場場均得分 Home PPG"
            value={stats.home_ppg}
            diff={Number(stats.home_ppg || 0) - Number(stats.league_avg_home_ppg || 0)}
            leagueRank={stats.home_ppg_rank_league}
            conferenceRank={stats.home_ppg_rank_conference}
          />
          <MetricBox
            label="主場場均失分 Home Opp PPG"
            value={stats.home_opp_ppg}
            diff={Number(stats.home_opp_ppg || 0) - Number(stats.league_avg_home_opp_ppg || 0)}
            leagueRank={stats.home_opp_ppg_rank_league}
            conferenceRank={stats.home_opp_ppg_rank_conference}
            lowerIsBetter
          />
        </div>
      </div>
    </section>
  )
}
