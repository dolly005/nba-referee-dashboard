import { Route, Routes } from 'react-router-dom'
import { apiGet } from './api/client'
import Layout from './components/Layout'
import Skeleton from './components/Skeleton'
import ArenaRefereePage from './pages/ArenaRefereePage'
import LeagueRankingsPage from './pages/LeagueRankingsPage'
import MatchupRefereePage from './pages/MatchupRefereePage'
import RefereesPage from './pages/RefereesPage'
import TeamRefereePage from './pages/TeamRefereePage'
import { useFetch } from './hooks'

export default function App() {
  const seasonsState = useFetch(() => apiGet('/api/seasons'), [])
  const teamsState = useFetch(() => apiGet('/api/teams'), [])
  const arenasState = useFetch(() => apiGet('/api/arenas'), [])
  const gameTypesState = useFetch(() => apiGet('/api/game-types'), [])
  const postseasonStagesState = useFetch(() => apiGet('/api/postseason-stages'), [])

  const bootLoading = seasonsState.loading || teamsState.loading || arenasState.loading || gameTypesState.loading || postseasonStagesState.loading
  const bootError = seasonsState.error || teamsState.error || arenasState.error || gameTypesState.error || postseasonStagesState.error

  if (bootLoading) {
    return <div className="min-h-screen bg-navy p-6"><Skeleton rows={12} /></div>
  }

  if (bootError) {
    return <div className="min-h-screen bg-navy p-8 text-nbaRed">API 連線失敗：{bootError.message}</div>
  }

  const common = {
    seasons: seasonsState.data,
    gameTypes: gameTypesState.data,
    postseasonStages: postseasonStagesState.data,
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<RefereesPage {...common} />} />
        <Route path="team-referee" element={<TeamRefereePage {...common} teams={teamsState.data} />} />
        <Route path="arena-referee" element={<ArenaRefereePage {...common} arenas={arenasState.data} />} />
        <Route path="matchup-referee" element={<MatchupRefereePage {...common} teams={teamsState.data} />} />
        <Route path="league-rankings" element={<LeagueRankingsPage {...common} />} />
      </Route>
    </Routes>
  )
}
