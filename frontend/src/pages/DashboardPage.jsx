import { RefreshCw, Clock } from 'lucide-react'
import { useMarketData } from '../hooks/useMarketData'
import ErrorAlert from '../components/common/ErrorAlert'
import PriceCard from '../components/dashboard/PriceCard'
import KimchiPremiumCard from '../components/dashboard/KimchiPremiumCard'
import FearGreedCard from '../components/dashboard/FearGreedCard'
import FeeRatesCard from '../components/dashboard/FeeRatesCard'
import NetworkStatsCard from '../components/dashboard/NetworkStatsCard'
import DashboardSkeleton from '../components/dashboard/DashboardSkeleton'

function formatUpdatedAt(isoString) {
  if (!isoString) return null
  const date = new Date(isoString)
  return date.toLocaleTimeString('ko-KR', {
    timeZone: 'Asia/Seoul',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export default function DashboardPage() {
  const { data, loading, error, refresh } = useMarketData()

  return (
    <div className="max-w-screen-xl mx-auto px-2 sm:px-4 md:px-6 py-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg font-semibold text-white">Data</h1>
        <div className="flex items-center gap-3">
          {data?.updated_at && (
            <div className="flex items-center gap-1 text-xs text-zinc-500">
              <Clock className="w-3 h-3" />
              <span>{formatUpdatedAt(data.updated_at)}</span>
            </div>
          )}
          <button
            onClick={refresh}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
            aria-label="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {error && <ErrorAlert message={error} />}

      {loading && !data ? (
        <DashboardSkeleton />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <PriceCard
            krwData={data?.bitcoin_price_krw}
            usdData={data?.bitcoin_price_usd}
          />
          <KimchiPremiumCard
            premium={data?.kimchi_premium}
            usdKrwRate={data?.usd_krw_rate}
          />
          <FearGreedCard fearGreed={data?.fear_greed_index} />
          <FeeRatesCard feeRates={data?.fee_rates} />
          <NetworkStatsCard
            difficulty={data?.difficulty_adjustment}
            hashrate={data?.hashrate}
            mempool={data?.mempool_stats}
            halving={data?.halving}
          />
        </div>
      )}
    </div>
  )
}
