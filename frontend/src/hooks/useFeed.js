import { useState, useEffect, useCallback } from 'react'
import { feedApi, bookmarkApi } from '../api/feed'
import { extractApiError } from '../api/client'

export function useFeed(options = {}) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hasNext, setHasNext] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null)

  const fetchFeed = useCallback(async (pageNum = 1, append = false) => {
    try {
      setLoading(true)
      setError(null)
      const data = await feedApi.getList({
        page: pageNum,
        pageSize: options.pageSize || 20,
        category: options.category,
        source: options.source,
        search: options.search,
      })

      setItems(prev => append ? [...prev, ...data.items] : data.items)
      setHasNext(data.has_next)
      setTotal(data.total)
      setPage(pageNum)
      if (data.last_updated_at) setLastUpdatedAt(data.last_updated_at)
    } catch (err) {
      setError(extractApiError(err))
    } finally {
      setLoading(false)
    }
  }, [options.category, options.source, options.search, options.pageSize])

  const loadMore = useCallback(() => {
    if (hasNext && !loading) {
      fetchFeed(page + 1, true)
    }
  }, [hasNext, loading, page, fetchFeed])

  const refresh = useCallback(() => {
    return fetchFeed(1, false)
  }, [fetchFeed])

  const toggleBookmark = useCallback(async (itemId) => {
    const item = items.find(i => i.id === itemId)
    if (!item) return

    try {
      if (item.is_bookmarked) {
        await bookmarkApi.remove(itemId)
      } else {
        await bookmarkApi.add(itemId)
      }

      // 로컬 상태 업데이트
      setItems(prev => prev.map(i =>
        i.id === itemId ? { ...i, is_bookmarked: !i.is_bookmarked } : i
      ))
    } catch (err) {
      console.error('Bookmark toggle failed:', err)
    }
  }, [items])

  useEffect(() => {
    fetchFeed(1)
  }, [fetchFeed])

  return {
    items,
    loading,
    error,
    hasNext,
    total,
    page,
    lastUpdatedAt,
    loadMore,
    refresh,
    toggleBookmark,
  }
}

/**
 * 마운트 시 1회 fetch하는 공통 패턴
 */
function useFetchOnMount(fetchFn, initialValue = []) {
  const [data, setData] = useState(initialValue)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const run = async () => {
      try {
        const result = await fetchFn()
        if (!cancelled) setData(result)
      } catch (err) {
        console.error('Fetch failed:', err)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    run()
    return () => { cancelled = true }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return { data, loading }
}

export function useTrending() {
  const { data, loading } = useFetchOnMount(() => feedApi.getTrending(5))
  return { items: data, loading }
}

export function useCategories() {
  const { data, loading } = useFetchOnMount(() => feedApi.getCategories())
  return { categories: data, loading }
}

export function useSources() {
  const { data, loading } = useFetchOnMount(() => feedApi.getSources())
  return { sources: data, loading }
}

export function useBookmarks() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchBookmarks = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await bookmarkApi.getList()
      setItems(data.items || [])
    } catch (err) {
      setError(extractApiError(err))
    } finally {
      setLoading(false)
    }
  }, [])

  const removeBookmark = useCallback(async (itemId) => {
    try {
      await bookmarkApi.remove(itemId)
      setItems(prev => prev.filter(b => b.item.id !== itemId))
    } catch (err) {
      console.error('Failed to remove bookmark:', err)
    }
  }, [])

  useEffect(() => {
    fetchBookmarks()
  }, [fetchBookmarks])

  return { items, loading, error, refresh: fetchBookmarks, removeBookmark }
}

export function useSchedulerStatus() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchStatus = useCallback(async () => {
    try {
      const data = await feedApi.getSchedulerStatus()
      setStatus(data)
    } catch (err) {
      console.error('Failed to fetch scheduler status:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    // 1분마다 상태 업데이트
    const interval = setInterval(fetchStatus, 60000)
    return () => clearInterval(interval)
  }, [fetchStatus])

  return { status, loading, refresh: fetchStatus }
}

export function useFetchProgress() {
  const [progress, setProgress] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchProgress = useCallback(async () => {
    try {
      const data = await feedApi.getFetchProgress()
      setProgress(data)
      return data
    } catch (err) {
      console.error('Failed to fetch progress:', err)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // 즉시 첫 번째 호출
    fetchProgress()

    // 2초마다 폴링 (수집 중일 때 실시간 업데이트)
    const intervalId = setInterval(fetchProgress, 2000)

    return () => clearInterval(intervalId)
  }, [fetchProgress])

  return { progress, loading, refresh: fetchProgress }
}
