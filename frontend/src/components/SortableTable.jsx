import { useMemo, useState } from 'react'
import EmptyState from './EmptyState'

export default function SortableTable({ columns, rows, defaultSortKey, defaultDirection = 'desc' }) {
  const [sortKey, setSortKey] = useState(defaultSortKey || columns[0]?.key)
  const [direction, setDirection] = useState(defaultDirection)

  const sortedRows = useMemo(() => {
    return [...rows].sort((a, b) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      if (typeof av === 'number' && typeof bv === 'number') return direction === 'asc' ? av - bv : bv - av
      return direction === 'asc'
        ? String(av ?? '').localeCompare(String(bv ?? ''))
        : String(bv ?? '').localeCompare(String(av ?? ''))
    })
  }, [rows, sortKey, direction])

  function toggle(key) {
    if (sortKey === key) setDirection(direction === 'asc' ? 'desc' : 'asc')
    else {
      setSortKey(key)
      setDirection('desc')
    }
  }

  if (!rows.length) return <EmptyState />

  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-panel shadow-glow">
      <div className="table-scroll overflow-x-auto">
        <table className="min-w-full divide-y divide-white/10 text-left text-sm">
          <thead className="bg-white/5 text-xs uppercase tracking-wider text-slate-300">
            <tr>
              <th className="w-16 px-5 py-4">#</th>
              {columns.map((col) => (
                <th key={col.key} className="px-5 py-4">
                  <button type="button" onClick={() => toggle(col.key)} className="flex items-center gap-2 font-bold hover:text-white">
                    {col.label}
                    {sortKey === col.key && <span className="text-nbaRed">{direction === 'asc' ? '▲' : '▼'}</span>}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {sortedRows.map((row, index) => (
              <tr key={`${row.official_id || row.id}-${index}`} className={index < 3 ? 'bg-nbaRed/10' : 'hover:bg-white/[0.03]'}>
                <td className="px-5 py-4 font-semibold text-slate-400">{index + 1}</td>
                {columns.map((col) => (
                  <td key={col.key} className="px-5 py-4 text-slate-100">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
