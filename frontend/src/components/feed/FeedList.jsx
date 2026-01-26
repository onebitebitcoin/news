import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import FeedCard from './FeedCard'
import SkeletonLoader from '../common/SkeletonLoader'

export default function FeedList({ items, loading, onBookmark, onLoadMore, hasNext }) {
  const [expanded, setExpanded] = useState({})

  if (loading && items.length === 0) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <SkeletonLoader key={i} />
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-zinc-500">No news found</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {items.map((item) => {
        const isExpanded = expanded[item.id]
        const hasDuplicates = item.duplicate_count > 0

        return (
          <div key={item.id} className="space-y-2">
            <FeedCard item={item} onBookmark={onBookmark} />
            {hasDuplicates && (
              <button
                onClick={() =>
                  setExpanded((prev) => ({ ...prev, [item.id]: !prev[item.id] }))
                }
                className="w-full flex items-center justify-between px-3 py-2 text-sm text-zinc-300 bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 transition-colors"
              >
                <span>유사 기사 {item.duplicate_count}개</span>
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>
            )}
            {hasDuplicates && isExpanded && (
              <div className="border border-zinc-800 rounded-lg divide-y divide-zinc-800 bg-zinc-950">
                {item.duplicates.map((dup) => (
                  <a
                    key={dup.id}
                    href={dup.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block px-3 py-2 text-sm text-zinc-300 hover:bg-zinc-900 transition-colors"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="line-clamp-1">{dup.title}</span>
                      <span className="text-xs text-zinc-500 shrink-0">{dup.source}</span>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>
        )
      })}

      {/* Load More */}
      {hasNext && (
        <div className="py-4 text-center">
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="px-6 py-2.5 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}
    </div>
  )
}
