export function pct(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '0%'
  return `${Math.round(Number(value))}%`
}

export function pctDecimal(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '0%'
  return `${Math.round(Number(value) * 100)}%`
}

export function oneDecimal(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '0.0'
  return Number(value).toFixed(1)
}

export function signedOneDecimal(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '+0.0'
  const n = Number(value)
  return `${n >= 0 ? '+' : ''}${n.toFixed(1)}`
}

export function winRateWithRecord(rate, wins, losses) {
  return { rate: pct(rate), record: `${wins ?? 0}W-${losses ?? 0}L` }
}

export function winRateDecimalWithRecord(rate, wins, losses) {
  return { rate: pctDecimal(rate), record: `${wins ?? 0}W-${losses ?? 0}L` }
}
