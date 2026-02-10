import { ArrowUpDown } from 'lucide-react'

function getPremiumColor(value) {
  if (value == null) return 'text-zinc-400'
  if (value >= 5) return 'text-red-400'
  if (value >= 3) return 'text-amber-400'
  if (value >= 0) return 'text-emerald-400'
  return 'text-blue-400'
}

function getPremiumLabel(value) {
  if (value == null) return '-'
  if (value >= 5) return 'High'
  if (value >= 3) return 'Moderate'
  if (value >= 0) return 'Normal'
  return 'Discount'
}

const formatRate = (value) => {
  if (!value) return '-'
  return new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 1 }).format(value)
}

export default function KimchiPremiumCard({ premium, usdtKrwRate }) {
  const color = getPremiumColor(premium)
  const label = getPremiumLabel(premium)

  return (
    <div className="bg-zinc-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-zinc-400 text-sm font-medium">Kimchi Premium</span>
        <ArrowUpDown className="w-4 h-4 text-zinc-500" />
      </div>

      <div className="mb-3">
        <div className={`text-2xl font-bold ${color}`}>
          {premium != null ? `${premium >= 0 ? '+' : ''}${premium}%` : '-'}
        </div>
        <div className={`text-sm mt-0.5 ${color}`}>
          {label}
        </div>
      </div>

      <div className="text-xs">
        <span className="text-zinc-500">USDT/KRW</span>
        <div className="text-zinc-300 mt-0.5">{formatRate(usdtKrwRate)} KRW</div>
      </div>
    </div>
  )
}
