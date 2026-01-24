import { useState, useEffect, useCallback } from 'react'
import { feedApi, bookmarkApi } from '../api/feed'

export function useFeed(options = {}) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hasNext, setHasNext] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)

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
    } catch (err) {
      setError(err.message || 'Failed to fetch feed')
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
    fetchFeed(1, false)
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
    loadMore,
    refresh,
    toggleBookmark,
  }
}

export function useTrending() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const data = await feedApi.getTrending(5)
        setItems(data)
      } catch (err) {
        console.error('Failed to fetch trending:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchTrending()
  }, [])

  return { items, loading }
}

export function useCategories() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await feedApi.getCategories()
        setCategories(data)
      } catch (err) {
        console.error('Failed to fetch categories:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchCategories()
  }, [])

  return { categories, loading }
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
      setError(err.message || 'Failed to fetch bookmarks')
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
