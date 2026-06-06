import { pctDecimal } from '../utils/format'

export default function SummaryBanner({ summary }) {
  const data = summary || {}
  return (
    <section className="mb-5 grid grid-cols-1 gap-4 rounded-3xl border border-white/10 bg-gradient-to-br from-panel2 to-panel p-6 shadow-glow md:grid-cols-[1.2fr_1fr]">
      <div>
        <p className="text-sm text-slate-400">本賽季聯盟整體主場勝率</p>
        <p className="mt-2 text-6xl font-black tracking-tight text-nbaRed">{pctDecimal(data.overall_home_win_rate)}</p>
        <p className="mt-2 text-sm text-slate-300">（{data.home_wins ?? 0}W-{data.home_losses ?? 0}L，共 {data.total_games ?? 0} 場）</p>
      </div>
      <div className="grid content-center gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
        <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Coverage</p>
        <p className="text-2xl font-black text-white">共 {data.total_referees ?? 0} 位裁判</p>
        <p className="text-2xl font-black text-white">共 {data.total_games ?? 0} 場比賽</p>
      </div>
    </section>
  )
}
