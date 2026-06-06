import { NavLink, Outlet } from 'react-router-dom'
import { Activity } from 'lucide-react'

const navItems = [
  { to: '/', label: '裁判名單' },
  { to: '/team-referee', label: '球隊 × 裁判' },
  { to: '/arena-referee', label: '場館 × 裁判' },
  { to: '/matchup-referee', label: '對戰組合 × 裁判' },
  { to: '/league-rankings', label: '聯盟排名' },
]

export default function Layout() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#17315a_0,#07111f_42%)] text-white">
      <header className="sticky top-0 z-30 border-b border-white/10 bg-navy/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-2xl bg-nbaRed shadow-glow">
              <Activity className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">NBA Referee Dashboard</h1>
              <p className="text-xs text-slate-400">2021-22 至今｜例行賽與季後賽裁判分析</p>
            </div>
          </div>
          <nav className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-full px-4 py-2 text-sm font-medium transition ${isActive ? 'bg-white text-navy' : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
