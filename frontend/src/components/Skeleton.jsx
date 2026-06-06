export default function Skeleton({ rows = 8 }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-panel p-5 shadow-glow">
      <div className="mb-4 h-8 w-48 animate-pulse rounded-xl bg-white/10" />
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-12 animate-pulse rounded-2xl bg-white/10" />
        ))}
      </div>
    </div>
  )
}
