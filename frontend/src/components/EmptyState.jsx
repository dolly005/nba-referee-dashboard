export default function EmptyState({ title = '查無資料', message = '目前篩選條件沒有對應資料，請改選其他賽季、球隊或場館。' }) {
  return (
    <div className="rounded-3xl border border-dashed border-white/15 bg-panel p-10 text-center shadow-glow">
      <h3 className="text-xl font-bold text-white">{title}</h3>
      <p className="mt-2 text-sm text-slate-400">{message}</p>
    </div>
  )
}
