import { Gauge } from 'lucide-react'

function getGaugeColor(value) {
  if (value == null) return { bar: 'bg-zinc-700', text: 'text-zinc-400' }
  if (value <= 25) return { bar: 'bg-red-500', text: 'text-red-400' }
  if (value <= 50) return { bar: 'bg-orange-500', text: 'text-orange-400' }
  if (value <= 75) return { bar: 'bg-emerald-500', text: 'text-emerald-400' }
  return { bar: 'bg-green-500', text: 'text-green-400' }
}

export default function FearGreedCard({ fearGreed }) {
  const value = fearGreed?.value
  const classification = fearGreed?.classification || '-'
  const colors = getGaugeColor(value)
  const percent = value != null ? value : 0

  return (
    <div className="bg-zinc-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-zinc-400 text-sm font-medium">Fear & Greed</span>
        <Gauge className="w-4 h-4 text-zinc-500" />
      </div>

      <div className="flex items-baseline gap-2 mb-3">
        <span className={`text-2xl font-bold ${colors.text}`}>
          {value != null ? value : '-'}
        </span>
        <span className={`text-sm ${colors.text}`}>
          {classification}
        </span>
      </div>

      <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${colors.bar}`}
          style={{ width: `${percent}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-zinc-600 mt-1">
        <span>Fear</span>
        <span>Greed</span>
      </div>
    </div>
  )
}
