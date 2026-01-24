import FeedCard from './FeedCard'
import SkeletonLoader from '../common/SkeletonLoader'

export default function FeedList({ items, loading, onBookmark, onLoadMore, hasNext }) {
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
      {items.map((item) => (
        <FeedCard key={item.id} item={item} onBookmark={onBookmark} />
      ))}

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
