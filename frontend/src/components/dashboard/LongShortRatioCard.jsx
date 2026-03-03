import { TrendingUp } from 'lucide-react'

function getSentimentLabel(ratio) {
  if (ratio == null) return '-'
  if (ratio >= 1.5) return 'Greed'
  if (ratio >= 1.1) return 'Bullish'
  if (ratio >= 0.9) return 'Neutral'
  if (ratio >= 0.7) return 'Bearish'
  return 'Fear'
}

function getSentimentColor(ratio) {
  if (ratio == null) return 'text-zinc-400'
  if (ratio >= 1.5) return 'text-amber-400'
  if (ratio >= 1.1) return 'text-emerald-400'
  if (ratio >= 0.9) return 'text-zinc-300'
  if (ratio >= 0.7) return 'text-orange-400'
  return 'text-red-400'
}

export default function LongShortRatioCard({ longShortRatio }) {
  const ratio = longShortRatio?.long_short_ratio ?? null
  const longPct = longShortRatio?.long_account ?? null
  const shortPct = longShortRatio?.short_account ?? null

  const color = getSentimentColor(ratio)
  const label = getSentimentLabel(ratio)

  return (
    <div className="bg-zinc-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-zinc-400 text-sm font-medium">Long/Short Ratio</span>
        <TrendingUp className="w-4 h-4 text-zinc-500" />
      </div>

      <div className="mb-3">
        <div className={`text-2xl font-bold ${color}`}>
          {ratio != null ? ratio.toFixed(2) : '-'}
        </div>
        <div className={`text-sm mt-0.5 ${color}`}>
          {label}
        </div>
      </div>

      {longPct != null && shortPct != null && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="text-emerald-400">Long {longPct.toFixed(1)}%</span>
            <span className="text-red-400">Short {shortPct.toFixed(1)}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all"
              style={{ width: `${longPct}%` }}
            />
          </div>
        </div>
      )}

      <div className="text-xs text-zinc-500 mt-2">
        Binance 선물 글로벌 계좌 기준 (1h)
      </div>
    </div>
  )
}
