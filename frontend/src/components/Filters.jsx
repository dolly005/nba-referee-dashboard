const GAME_TYPE_LABELS = {
  'Regular Season': '例行賽',
  Playoffs: '季後賽',
  '全部賽事': '全部賽事',
}

const STAGE_LABELS = {
  '全部階段': '全部階段',
  'First Round': '第一輪',
  'Conference Semifinals': '第二輪',
  'Conference Finals': '分區冠軍賽',
  'NBA Finals': '總冠軍賽',
}

export default function Filters({
  season,
  setSeason,
  gameType,
  setGameType,
  seasons = [],
  gameTypes = [],
  postseasonStage = '全部階段',
  setPostseasonStage,
  postseasonStages = [],
}) {
  const seasonOptions = ['所有賽季', ...seasons]
  const typeOptions = ['全部賽事', ...(gameTypes.length ? gameTypes : ['Regular Season', 'Playoffs'])]
  const stageOptions = ['全部階段', ...(postseasonStages.length ? postseasonStages : ['First Round', 'Conference Semifinals', 'Conference Finals', 'NBA Finals'])]
  const showStage = gameType !== 'Regular Season' && Boolean(setPostseasonStage)

  function changeGameType(type) {
    setGameType(type)
    if (type === 'Regular Season' && setPostseasonStage) setPostseasonStage('全部階段')
  }

  return (
    <section className="mb-6 rounded-3xl border border-white/10 bg-panel/90 p-4 shadow-glow">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Current Filter</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <span className="inline-flex items-center rounded-full bg-nbaRed px-4 py-2 text-sm font-bold text-white">
              賽季：{season}
            </span>
            <span className="inline-flex items-center rounded-full bg-nbaBlue px-4 py-2 text-sm font-bold text-white">
              賽事：{GAME_TYPE_LABELS[gameType] || gameType}
            </span>
            {showStage && (
              <span className="inline-flex items-center rounded-full bg-white/10 px-4 py-2 text-sm font-bold text-white">
                階段：{STAGE_LABELS[postseasonStage] || postseasonStage}
              </span>
            )}
          </div>
        </div>
        <div className={`grid grid-cols-1 gap-3 ${showStage ? 'sm:grid-cols-3' : 'sm:grid-cols-2'}`}>
          <label className="text-sm text-slate-300">
            賽季選擇器
            <select
              value={season}
              onChange={(e) => setSeason(e.target.value)}
              className="mt-1 w-full rounded-2xl border border-white/10 bg-navy px-4 py-3 text-white outline-none focus:border-nbaRed"
            >
              {seasonOptions.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </label>
          <label className="text-sm text-slate-300">
            賽事類別
            <div className="mt-1 flex flex-wrap gap-2">
              {typeOptions.map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => changeGameType(type)}
                  className={`rounded-2xl px-4 py-3 text-sm font-semibold ${gameType === type ? 'bg-nbaBlue text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}
                >
                  {GAME_TYPE_LABELS[type] || type}
                </button>
              ))}
            </div>
          </label>
          {showStage && (
            <label className="text-sm text-slate-300">
              季後賽階段
              <select
                value={postseasonStage}
                onChange={(e) => setPostseasonStage(e.target.value)}
                className="mt-1 w-full rounded-2xl border border-white/10 bg-navy px-4 py-3 text-white outline-none focus:border-nbaRed"
              >
                {stageOptions.map((stage) => <option key={stage} value={stage}>{STAGE_LABELS[stage] || stage}</option>)}
              </select>
            </label>
          )}
        </div>
      </div>
    </section>
  )
}
