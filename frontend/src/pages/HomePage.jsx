import { useState, useCallback, useMemo, useRef, useEffect } from 'react'
import { CheckCircle2, RefreshCw, XCircle } from 'lucide-react'
import ErrorAlert from '../components/common/ErrorAlert'
import TrendingSection from '../components/feed/TrendingSection'
import CategoryChips from '../components/filters/CategoryChips'
import SearchBar from '../components/filters/SearchBar'
import SourceSelect from '../components/filters/SourceSelect'
import FeedList from '../components/feed/FeedList'
import { feedApi } from '../api/feed'
import { useFeed, useCategories, useFetchProgress, useSchedulerStatus, useSources } from '../hooks/useFeed'
import { getTimeAgo } from '../utils/dateUtils'

export default function HomePage() {
  const [category, setCategory] = useState(null)
  const [source, setSource] = useState(null)
  const [search, setSearch] = useState('')
  const [refreshNotice, setRefreshNotice] = useState(null)
  const [manualRefreshing, setManualRefreshing] = useState(false)
  const noticeTimeoutRef = useRef(null)

  const { categories } = useCategories()
  const { sources } = useSources()
  const {
    items,
    loading,
    error,
    hasNext,
    loadMore,
    refresh,
    toggleBookmark,
  } = useFeed({ category, search, source })

  const { status: schedulerStatus, refresh: refreshScheduler } = useSchedulerStatus()
  const { progress: fetchProgress, loading: progressLoading, refresh: refreshProgress } = useFetchProgress()

  // 마지막 수집 시간 (상대 시간)
  const lastFetchText = useMemo(() => {
    if (!schedulerStatus?.last_fetch_at) return null
    return getTimeAgo(schedulerStatus.last_fetch_at)
  }, [schedulerStatus?.last_fetch_at])

  // 수집 중 여부
  const isFetching = fetchProgress?.status === 'running'
  const isProgressLoading = progressLoading && !fetchProgress

  // 새로고침 핸들러 (피드 + 스케줄러 상태 + 진행 상황 모두 갱신)
  const handleRefresh = useCallback(async () => {
    if (noticeTimeoutRef.current) {
      clearTimeout(noticeTimeoutRef.current)
    }

    setManualRefreshing(true)
    setRefreshNotice({ type: 'info', message: '수집을 시작합니다.' })

    try {
      const result = await feedApi.runFetch()
      // 병렬 실행으로 성능 개선
      await Promise.all([
        refreshProgress(),
        refreshScheduler(),
        refresh()
      ])

      const saved = result?.total_saved ?? 0
      setRefreshNotice({ type: 'success', message: `수집 완료. ${saved}개 저장됨.` })
    } catch (err) {
      const detailMessage = err?.response?.data?.detail?.message
      const message = detailMessage || '수집 요청에 실패했습니다.'
      setRefreshNotice({ type: 'error', message })
    } finally {
      setManualRefreshing(false)
      noticeTimeoutRef.current = setTimeout(() => {
        setRefreshNotice(null)
      }, 5000)
    }
  }, [refresh, refreshScheduler, refreshProgress])

  const handleCategoryChange = useCallback((newCategory) => {
    setCategory(newCategory)
  }, [])

  const handleSourceChange = useCallback((newSource) => {
    setSource(newSource)
  }, [])

  const handleSearch = useCallback((query) => {
    setSearch(query)
  }, [])

  useEffect(() => {
    return () => {
      if (noticeTimeoutRef.current) {
        clearTimeout(noticeTimeoutRef.current)
      }
    }
  }, [])

  return (
    <div className="max-w-screen-xl mx-auto px-4 sm:px-6">
      {/* Trending Section */}
      <TrendingSection />

      {/* Search Bar */}
      <div className="py-3">
        <SearchBar value={search} onChange={handleSearch} />
      </div>

      {/* Category Chips */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <CategoryChips
          categories={categories}
          selected={category}
          onChange={handleCategoryChange}
        />
        <SourceSelect
          sources={sources}
          selected={source}
          onChange={handleSourceChange}
        />
      </div>

      {/* Header */}
      <div className="flex items-center justify-between py-3">
        <div className="flex items-center gap-3">
          <h2 className="font-bold text-lg">최신 뉴스</h2>
          {isProgressLoading ? (
            <span className="text-sm text-zinc-500 flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-zinc-500 rounded-full animate-pulse" />
              상태 확인 중...
            </span>
          ) : isFetching ? (
            <span className="text-sm text-amber-500 flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
              수집 중... ({fetchProgress.current_source || '준비'} {fetchProgress.sources_completed}/{fetchProgress.sources_total})
              {fetchProgress.items_fetched > 0 && (
                <span className="text-zinc-500">
                  - {fetchProgress.items_fetched}개 조회, {fetchProgress.items_saved}개 저장
                </span>
              )}
            </span>
          ) : lastFetchText ? (
            <span className="text-sm text-zinc-500">
              마지막 수집: {lastFetchText}
            </span>
          ) : null}
        </div>
        <button
          onClick={handleRefresh}
          disabled={loading || manualRefreshing || isFetching}
          className="p-2 rounded-lg hover:bg-zinc-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 text-zinc-400 ${manualRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {refreshNotice && (
        <div className="mb-3 rounded-lg border px-3 py-2 flex items-center gap-2 text-sm">
          {refreshNotice.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
          {refreshNotice.type === 'error' && <XCircle className="w-4 h-4 text-red-400" />}
          {refreshNotice.type === 'info' && <RefreshCw className="w-4 h-4 text-amber-400" />}
          <span
            className={
              refreshNotice.type === 'success'
                ? 'text-emerald-400'
                : refreshNotice.type === 'error'
                  ? 'text-red-400'
                  : 'text-amber-400'
            }
          >
            {refreshNotice.message}
          </span>
        </div>
      )}

      {/* Error */}
      <ErrorAlert message={error} />

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
