import { winRateWithRecord } from '../utils/format'

export default function RateCell({ rate, wins, losses }) {
  const display = winRateWithRecord(rate, wins, losses)
  return (
    <span>
      <strong className="text-white">{display.rate}</strong>
      <span className="ml-1 text-slate-400">（{display.record}）</span>
    </span>
  )
}
