import { RefreshCw, BookmarkX } from 'lucide-react'
import ErrorAlert from '../components/common/ErrorAlert'
import FeedCard from '../components/feed/FeedCard'
import SkeletonLoader from '../components/common/SkeletonLoader'
import { useBookmarks } from '../hooks/useFeed'

export default function BookmarksPage() {
  const { items, loading, error, refresh, removeBookmark } = useBookmarks()

  return (
    <div className="max-w-screen-xl mx-auto px-2 sm:px-4 py-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold">Saved Articles</h1>
        <button
          onClick={refresh}
          disabled={loading}
          className="p-2 rounded-lg hover:bg-zinc-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 text-zinc-400 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Error */}
      <ErrorAlert message={error} onRetry={refresh} />

      {/* Loading */}
      {loading && items.length === 0 && (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <SkeletonLoader key={i} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && items.length === 0 && (
        <div className="text-center py-16">
          <BookmarkX className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-zinc-400 mb-2">No saved articles</h3>
          <p className="text-sm text-zinc-500">
            Articles you bookmark will appear here
          </p>
        </div>
      )}

      {/* Bookmarks List */}
      {items.length > 0 && (
        <div className="space-y-4">
          {items.map(({ bookmark, item }) => (
            <FeedCard
              key={bookmark.id}
              item={item}
              onBookmark={removeBookmark}
            />
          ))}
        </div>
      )}
    </div>
  )
}
