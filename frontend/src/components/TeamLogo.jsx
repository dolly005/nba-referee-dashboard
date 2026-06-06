import { logoUrl, teamByAbbr } from '../data/teamConfig'

export default function TeamLogo({ abbr, size = 'md', showAbbr = true, showName = false }) {
  const team = teamByAbbr[abbr]
  const sizes = {
    sm: 'h-7 w-7',
    md: 'h-10 w-10',
    lg: 'h-14 w-14',
  }
  return (
    <span className="inline-flex items-center gap-2" title={team?.fullName || abbr}>
      <span className={`grid ${sizes[size] || sizes.md} place-items-center rounded-full bg-white/90 p-1 shadow-sm`}>
        {team ? <img src={logoUrl(abbr)} alt={team.fullName} className="h-full w-full object-contain" /> : <span className="text-xs font-bold text-navy">{abbr}</span>}
      </span>
      {showAbbr && <span className="font-bold text-white">{abbr}</span>}
      {showName && <span className="hidden text-sm text-slate-300 sm:inline">{team?.fullName}</span>}
    </span>
  )
}
