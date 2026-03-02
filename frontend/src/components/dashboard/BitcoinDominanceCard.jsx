import { PieChart } from 'lucide-react'
import { formatDominancePercent } from '../../utils/formatUtils'

function getDominanceLabel(value) {
  if (value == null) return '-'
  if (value >= 55) return 'Dominant'
  if (value >= 50) return 'Strong'
  return 'Weakening'
}

function getDominanceColor(value) {
  if (value == null) return 'text-zinc-400'
  if (value >= 55) return 'text-amber-400'
  if (value >= 50) return 'text-emerald-400'
  return 'text-zinc-300'
}

export default function BitcoinDominanceCard({ dominance }) {
  const color = getDominanceColor(dominance)
  const label = getDominanceLabel(dominance)

  return (
    <div className="bg-zinc-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-zinc-400 text-sm font-medium">BTC Dominance</span>
        <PieChart className="w-4 h-4 text-zinc-500" />
      </div>

      <div className="mb-3">
        <div className={`text-2xl font-bold ${color}`}>
          {formatDominancePercent(dominance)}
        </div>
        <div className={`text-sm mt-0.5 ${color}`}>
          {label}
        </div>
      </div>

      <div className="text-xs text-zinc-500">
        전체 암호화폐 시가총액 대비 BTC 비중
      </div>
    </div>
  )
}
