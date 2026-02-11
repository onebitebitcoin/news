import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatKRW, formatUSD, formatPercent, formatVolume } from '../../utils/formatUtils'

export default function PriceCard({ krwData, usdData }) {
  const changeRate = krwData?.change_rate
  const isUp = changeRate > 0
  const isDown = changeRate < 0

  const changeColor = isUp ? 'text-emerald-400' : isDown ? 'text-red-400' : 'text-zinc-400'
  const ChangeIcon = isUp ? TrendingUp : isDown ? TrendingDown : Minus

  return (
    <div className="bg-zinc-900 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-zinc-400 text-sm font-medium">BTC Price</span>
        <div className={`flex items-center gap-1 text-sm ${changeColor}`}>
          <ChangeIcon className="w-4 h-4" />
          <span>{formatPercent(changeRate)}</span>
        </div>
      </div>

      <div className="mb-3">
        <div className="text-2xl font-bold text-white">
          {formatKRW(krwData?.price)}
        </div>
        <div className="text-zinc-400 text-sm mt-0.5">
          {formatUSD(usdData?.price)}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-xs">
        <div>
          <span className="text-zinc-500">High</span>
          <div className="text-zinc-300 mt-0.5">{formatKRW(krwData?.high_price)}</div>
        </div>
        <div>
          <span className="text-zinc-500">Low</span>
          <div className="text-zinc-300 mt-0.5">{formatKRW(krwData?.low_price)}</div>
        </div>
        <div>
          <span className="text-zinc-500">Vol(24h)</span>
          <div className="text-zinc-300 mt-0.5">{formatVolume(krwData?.acc_trade_volume_24h)} BTC</div>
        </div>
      </div>
    </div>
  )
}
