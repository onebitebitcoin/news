import { TrendingUp } from 'lucide-react'
import ErrorAlert from '../common/ErrorAlert'
import { useTrending } from '../../hooks/useFeed'

export default function TrendingSection() {
  const { items, loading, error, refresh } = useTrending()

  if (loading) {
    return (
      <div className="py-4">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-orange-500" />
          <span className="font-semibold text-sm">인기</span>
        </div>
        <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-2">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="flex-shrink-0 w-64 h-24 bg-zinc-800 rounded-lg animate-pulse"
            />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return <ErrorAlert message={error} onRetry={refresh} />
  }

  if (items.length === 0) return null

  return (
    <div className="py-4">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp className="w-4 h-4 text-orange-500" />
        <span className="font-semibold text-sm">인기</span>
      </div>
      <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-2 -mx-2 px-2">
        {items.map((item, index) => (
          <a
            key={item.id}
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-shrink-0 w-64 bg-zinc-900 rounded-lg p-3 hover:bg-zinc-800/80 transition-colors"
          >
            <div className="flex gap-3">
              <span className="text-2xl font-bold text-orange-500">
                {index + 1}
              </span>
              <div className="min-w-0">
                <p className="font-medium text-sm line-clamp-2 text-white">
                  {item.title}
                </p>
                <p className="text-xs text-zinc-500 mt-1">{item.source}</p>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
