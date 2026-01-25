import { useState, useCallback, useMemo } from 'react'
import { RefreshCw } from 'lucide-react'
import TrendingSection from '../components/feed/TrendingSection'
import CategoryChips from '../components/filters/CategoryChips'
import SearchBar from '../components/filters/SearchBar'
import FeedList from '../components/feed/FeedList'
import { useFeed, useCategories, useSchedulerStatus } from '../hooks/useFeed'

// 상대 시간 표시 함수
function getRelativeTime(dateString) {
  if (!dateString) return null

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMinutes < 1) return '방금 전'
  if (diffMinutes < 60) return `${diffMinutes}분 전`
  if (diffHours < 24) return `${diffHours}시간 전`
  return `${diffDays}일 전`
}

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

  const { status: schedulerStatus, refresh: refreshScheduler } = useSchedulerStatus()

  // 마지막 수집 시간 (상대 시간)
  const lastFetchText = useMemo(() => {
    if (!schedulerStatus?.last_fetch_at) return null
    return getRelativeTime(schedulerStatus.last_fetch_at)
  }, [schedulerStatus?.last_fetch_at])

  // 새로고침 핸들러 (피드 + 스케줄러 상태 모두 갱신)
  const handleRefresh = useCallback(() => {
    refresh()
    refreshScheduler()
  }, [refresh, refreshScheduler])

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
        <div className="flex items-center gap-3">
          <h2 className="font-bold text-lg">Latest News</h2>
          {lastFetchText && (
            <span className="text-sm text-zinc-500">
              마지막 수집: {lastFetchText}
            </span>
          )}
        </div>
        <button
          onClick={handleRefresh}
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
