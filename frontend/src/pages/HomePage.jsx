import { useState, useCallback } from 'react'
import { RefreshCw } from 'lucide-react'
import TrendingSection from '../components/feed/TrendingSection'
import CategoryChips from '../components/filters/CategoryChips'
import SearchBar from '../components/filters/SearchBar'
import FeedList from '../components/feed/FeedList'
import { useFeed, useCategories } from '../hooks/useFeed'

export default function HomePage() {
  const [category, setCategory] = useState(null)
  const [search, setSearch] = useState('')

  const { categories } = useCategories()
  const {
    items,
    loading,
    error,
    hasNext,
    loadMore,
    refresh,
    toggleBookmark,
  } = useFeed({ category, search })

  const handleCategoryChange = useCallback((newCategory) => {
    setCategory(newCategory)
  }, [])

  const handleSearch = useCallback((query) => {
    setSearch(query)
  }, [])

  return (
    <div className="max-w-screen-xl mx-auto px-2 sm:px-4">
      {/* Trending Section */}
      <TrendingSection />

      {/* Search Bar */}
      <div className="py-3">
        <SearchBar value={search} onChange={handleSearch} />
      </div>

      {/* Category Chips */}
      <CategoryChips
        categories={categories}
        selected={category}
        onChange={handleCategoryChange}
      />

      {/* Header */}
      <div className="flex items-center justify-between py-3">
        <h2 className="font-bold text-lg">Latest News</h2>
        <button
          onClick={refresh}
          disabled={loading}
          className="p-2 rounded-lg hover:bg-zinc-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 text-zinc-400 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-4">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Feed List */}
      <FeedList
        items={items}
        loading={loading}
        onBookmark={toggleBookmark}
        onLoadMore={loadMore}
        hasNext={hasNext}
      />
    </div>
  )
}
