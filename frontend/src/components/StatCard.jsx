import { pct } from '../utils/format'

export default function StatCard({ title, value, subtitle }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-panel2 to-panel p-6 shadow-glow">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-2 text-5xl font-black tracking-tight text-white">{typeof value === 'number' ? pct(value) : value}</p>
      {subtitle && <p className="mt-2 text-sm text-slate-300">{subtitle}</p>}
    </div>
  )
}
