import { Zap } from 'lucide-react'

const FEE_LEVELS = [
  { key: 'fastestFee', label: 'Fastest', color: 'text-red-400' },
  { key: 'halfHourFee', label: '30 min', color: 'text-amber-400' },
  { key: 'hourFee', label: '1 hour', color: 'text-emerald-400' },
  { key: 'economyFee', label: 'Economy', color: 'text-blue-400' },
]

export default function FeeRatesCard({ feeRates }) {
  return (
    <div className="bg-zinc-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-zinc-400 text-sm font-medium">Mempool Fees</span>
        <Zap className="w-4 h-4 text-zinc-500" />
      </div>

      <div className="space-y-2">
        {FEE_LEVELS.map(({ key, label, color }) => (
          <div key={key} className="flex items-center justify-between">
            <span className="text-zinc-400 text-sm">{label}</span>
            <span className={`text-sm font-medium ${color}`}>
              {feeRates?.[key] != null ? `${feeRates[key]} sat/vB` : '-'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
