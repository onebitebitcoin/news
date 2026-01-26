import { useState, useEffect } from 'react'
import { feedApi } from '../api/feed'

/**
 * 피드 아이템 상세 정보를 가져오는 훅
 * @param {string} id - 아이템 ID
 */
export function useItemDetail(id) {
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchItem = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await feedApi.getDetail(id)
        setItem(data)
      } catch (err) {
        setError(err.message || 'Failed to load article')
      } finally {
        setLoading(false)
      }
    }
    fetchItem()
  }, [id])

  const updateItem = (updates) => {
    setItem(prev => prev ? { ...prev, ...updates } : null)
  }

  return { item, loading, error, updateItem }
}
