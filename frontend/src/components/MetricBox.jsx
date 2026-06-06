import { oneDecimal, signedOneDecimal } from '../utils/format'

export default function MetricBox({
  label,
  value,
  diff,
  leagueRank,
  conferenceRank,
  suffix = '',
  lowerIsBetter = false,
}) {
  const numericDiff = Number(diff || 0)

  // 一般數據：高於平均為好，例如 PPG。
  // 失分數據：低於平均為好，例如 Opp PPG / Home Opp PPG。
  const isBetter = lowerIsBetter ? numericDiff <= 0 : numericDiff >= 0

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-4xl font-black text-white">{oneDecimal(value)}{suffix}</p>
      <div className="mt-3 space-y-1 text-sm">
        <p className={isBetter ? 'font-bold text-emerald-400' : 'font-bold text-nbaRed'}>
          {signedOneDecimal(diff)} vs 聯盟平均
        </p>
        <p className="text-slate-300">聯盟第 {leagueRank ?? '-'} 名</p>
        <p className="text-slate-300">分區第 {conferenceRank ?? '-'} 名</p>
      </div>
    </div>
  )
}