import TeamLogo from './TeamLogo'
import { groupTeams } from '../data/teamMeta'
import { teamByAbbr } from '../data/teamConfig'

export default function TeamGrid({ teams, selected, onSelect, disabledTeam }) {
  const normalizedTeams = teams.map((team) => ({
    ...team,
    full_name: team.full_name || teamByAbbr[team.abbreviation]?.fullName || team.abbreviation,
  }))
  const grouped = groupTeams(normalizedTeams)
  return (
    <div className="space-y-5">
      {Object.entries(grouped).map(([group, items]) => (
        <section key={group}>
          <h3 className="mb-2 text-xs font-bold uppercase tracking-[0.22em] text-slate-400">{group}</h3>
          <div className="grid grid-cols-3 gap-3 sm:grid-cols-5 lg:grid-cols-10">
            {items.map((team) => {
              const disabled = disabledTeam === team.abbreviation
              const active = selected === team.abbreviation
              return (
                <button
                  key={team.abbreviation}
                  type="button"
                  disabled={disabled}
                  title={team.full_name}
                  onClick={() => onSelect(team.abbreviation)}
                  className={`rounded-2xl border p-3 text-center transition ${active ? 'border-nbaRed bg-nbaRed/20' : 'border-white/10 bg-white/5 hover:bg-white/10'} ${disabled ? 'cursor-not-allowed opacity-30 grayscale' : ''}`}
                >
                  <div className="flex justify-center">
                    <TeamLogo abbr={team.abbreviation} size="lg" showAbbr={false} />
                  </div>
                  <p className="mt-2 text-xs font-bold text-white">{team.abbreviation}</p>
                </button>
              )
            })}
          </div>
        </section>
      ))}
    </div>
  )
}
