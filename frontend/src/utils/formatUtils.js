/** 숫자 포맷팅 유틸리티 */

export const formatKRW = (value) => {
  if (!value) return '-'
  return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW', maximumFractionDigits: 0 }).format(value)
}

export const formatUSD = (value) => {
  if (!value) return '-'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
}

export const formatPercent = (value) => {
  if (value == null) return '-'
  const pct = (value * 100).toFixed(2)
  return value >= 0 ? `+${pct}%` : `${pct}%`
}

export const formatVolume = (value) => {
  if (!value) return '-'
  return new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 2 }).format(value)
}

export const formatRate = (value) => {
  if (!value) return '-'
  return new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 1 }).format(value)
}

export const formatDominancePercent = (value) => {
  if (value == null) return '-'
  return `${Number(value).toFixed(2)}%`
}

export function formatHashrate(hashrate) {
  if (hashrate == null) return '-'
  const eh = hashrate / 1e18
  return `${eh.toFixed(1)} EH/s`
}

export function formatVsizeMB(vsize) {
  if (vsize == null) return '-'
  const mb = vsize / 1_000_000
  return `${mb.toFixed(1)} MB`
}

export function formatDaysFromSeconds(seconds) {
  if (seconds == null) return '-'
  const days = Math.floor(seconds / 86400)
  return `${days.toLocaleString()}d`
}
